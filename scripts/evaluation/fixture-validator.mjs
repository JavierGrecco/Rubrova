import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const defaultFixturePath = fileURLToPath(
  new URL("../../docs/fixtures/platform-evaluation.json", import.meta.url)
);

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function integer(value, path, errors, minimum = 0) {
  if (!Number.isSafeInteger(value) || value < minimum) {
    errors.push(path + " debe ser un entero seguro mayor o igual a " + minimum + ".");
    return null;
  }
  return value;
}

function roundDiv(numerator, denominator) {
  return (numerator + denominator / 2n) / denominator;
}

function parseMilliQuantity(value) {
  if (typeof value !== "string" || !/^\d+(?:\.\d{1,3})?$/.test(value)) return null;
  const parts = value.split(".");
  const whole = Number(parts[0]);
  const fraction = Number((parts[1] || "").padEnd(3, "0"));
  const result = whole * 1000 + fraction;
  return Number.isSafeInteger(result) ? result : null;
}

function compare(actual, expected, path, errors) {
  if (actual !== expected) {
    errors.push(path + ": esperado " + expected + ", recibido " + actual + ".");
  }
}

export function validateFixture(data) {
  const errors = [];

  if (!isRecord(data)) {
    return { valid: false, errors: ["El documento raíz debe ser un objeto JSON."] };
  }

  compare(data.schemaVersion, 1, "schemaVersion", errors);
  compare(data.dataClassification, "synthetic-no-personal-data", "dataClassification", errors);
  compare(data.locale, "es-AR", "locale", errors);
  compare(data.timeZone, "America/Argentina/Cordoba", "timeZone", errors);
  compare(data.currency, "ARS", "currency", errors);
  compare(data.moneyRepresentation, "integer-minor-units", "moneyRepresentation", errors);
  compare(data.minorUnitDigits, 2, "minorUnitDigits", errors);

  if (!Array.isArray(data.catalog) || data.catalog.length === 0) {
    errors.push("catalog debe contener al menos un artículo.");
    return { valid: false, errors };
  }

  const catalogBySku = new Map();
  const barcodes = new Set();

  for (const [index, item] of data.catalog.entries()) {
    const path = "catalog[" + index + "]";
    if (!isRecord(item)) {
      errors.push(path + " debe ser un objeto.");
      continue;
    }
    if (typeof item.sku !== "string" || item.sku.trim() === "") {
      errors.push(path + ".sku es obligatorio.");
      continue;
    }
    if (catalogBySku.has(item.sku)) errors.push("SKU duplicado: " + item.sku + ".");
    catalogBySku.set(item.sku, item);

    if (typeof item.barcode !== "string" || item.barcode.trim() === "") {
      errors.push(path + ".barcode es obligatorio.");
    } else if (barcodes.has(item.barcode)) {
      errors.push("Código de barras duplicado: " + item.barcode + ".");
    } else {
      barcodes.add(item.barcode);
    }

    integer(item.openingStockMilli, path + ".openingStockMilli", errors);
    if (!["unit", "kg"].includes(item.saleUnit)) {
      errors.push(path + ".saleUnit debe ser unit o kg.");
    }
  }

  const scenarios = data.scenarios;
  if (!isRecord(scenarios)) {
    errors.push("scenarios debe ser un objeto.");
    return { valid: false, errors };
  }

  const sale = scenarios.mixedPaymentSale;
  if (!isRecord(sale) || !Array.isArray(sale.lines) || sale.lines.length === 0) {
    errors.push("scenarios.mixedPaymentSale debe incluir líneas de venta.");
    return { valid: false, errors };
  }

  let subtotalMinor = 0n;
  let discountMinor = 0n;
  let totalMinor = 0n;
  const soldBySku = new Map();

  for (const [index, line] of sale.lines.entries()) {
    const path = "scenarios.mixedPaymentSale.lines[" + index + "]";
    if (!isRecord(line)) {
      errors.push(path + " debe ser un objeto.");
      continue;
    }

    if (!catalogBySku.has(line.sku)) errors.push(path + ".sku no existe en catalog.");
    const quantityMilli = integer(line.quantityMilli, path + ".quantityMilli", errors, 1);
    const unitPriceMinor = integer(line.unitPriceMinor, path + ".unitPriceMinor", errors);
    const discountPercent = integer(line.discountPercent, path + ".discountPercent", errors);
    const expectedLineTotalMinor = integer(
      line.expectedLineTotalMinor,
      path + ".expectedLineTotalMinor",
      errors
    );

    if (
      quantityMilli === null ||
      unitPriceMinor === null ||
      discountPercent === null ||
      expectedLineTotalMinor === null
    ) {
      continue;
    }
    if (discountPercent > 100) {
      errors.push(path + ".discountPercent no puede superar 100.");
      continue;
    }

    const gross = roundDiv(BigInt(unitPriceMinor) * BigInt(quantityMilli), 1000n);
    const net = roundDiv(gross * BigInt(100 - discountPercent), 100n);
    compare(expectedLineTotalMinor, Number(net), path + ".expectedLineTotalMinor", errors);

    if (discountPercent > 0) {
      const expectedLineDiscount = integer(
        line.expectedDiscountMinor,
        path + ".expectedDiscountMinor",
        errors
      );
      if (expectedLineDiscount !== null) {
        compare(expectedLineDiscount, Number(gross - net), path + ".expectedDiscountMinor", errors);
      }
    }

    subtotalMinor += gross;
    discountMinor += gross - net;
    totalMinor += net;
    soldBySku.set(line.sku, (soldBySku.get(line.sku) || 0) + quantityMilli);
  }

  const expectedSubtotal = integer(sale.expectedSubtotalMinor, "mixedPaymentSale.expectedSubtotalMinor", errors);
  const expectedDiscount = integer(sale.expectedDiscountMinor, "mixedPaymentSale.expectedDiscountMinor", errors);
  const expectedTotal = integer(sale.expectedTotalMinor, "mixedPaymentSale.expectedTotalMinor", errors);

  if (expectedSubtotal !== null) compare(expectedSubtotal, Number(subtotalMinor), "mixedPaymentSale.expectedSubtotalMinor", errors);
  if (expectedDiscount !== null) compare(expectedDiscount, Number(discountMinor), "mixedPaymentSale.expectedDiscountMinor", errors);
  if (expectedTotal !== null) compare(expectedTotal, Number(totalMinor), "mixedPaymentSale.expectedTotalMinor", errors);

  if (!Array.isArray(sale.payments) || sale.payments.length < 2) {
    errors.push("mixedPaymentSale.payments debe incluir al menos dos medios.");
  } else {
    let paymentTotal = 0;
    let cashTotal = 0;
    let cashMethods = 0;
    let transferMethods = 0;

    for (const [index, payment] of sale.payments.entries()) {
      const path = "mixedPaymentSale.payments[" + index + "]";
      if (!isRecord(payment)) {
        errors.push(path + " debe ser un objeto.");
        continue;
      }
      const amount = integer(payment.amountMinor, path + ".amountMinor", errors, 1);
      if (amount !== null) {
        paymentTotal += amount;
        if (payment.method === "cash") {
          cashTotal += amount;
          cashMethods += 1;
        }
        if (payment.method === "bank-transfer-simulated") transferMethods += 1;
      }
    }

    if (expectedTotal !== null) compare(paymentTotal, expectedTotal, "mixedPaymentSale.payments total", errors);
    compare(cashMethods, 1, "mixedPaymentSale cantidad de pagos en efectivo", errors);
    compare(transferMethods, 1, "mixedPaymentSale cantidad de transferencias simuladas", errors);

    const openingCash = integer(
      data.cashRegister?.openingCashMinor,
      "cashRegister.openingCashMinor",
      errors
    );
    const cashChange = integer(sale.expectedCashChangeMinor, "mixedPaymentSale.expectedCashChangeMinor", errors);
    const expectedCashAfterSale = integer(
      sale.expectedRegisterCashAfterSaleMinor,
      "mixedPaymentSale.expectedRegisterCashAfterSaleMinor",
      errors
    );
    if (openingCash !== null && cashChange !== null && expectedCashAfterSale !== null) {
      compare(
        expectedCashAfterSale,
        openingCash + cashTotal - cashChange,
        "mixedPaymentSale.expectedRegisterCashAfterSaleMinor",
        errors
      );
    }
  }

  const weighted = scenarios.weightedSale;
  if (!isRecord(weighted)) {
    errors.push("scenarios.weightedSale debe ser un objeto.");
  } else {
    if (!catalogBySku.has(weighted.sku)) errors.push("weightedSale.sku no existe en catalog.");
    const quantityMilli = parseMilliQuantity(weighted.quantity);
    if (quantityMilli === null) {
      errors.push("weightedSale.quantity debe ser decimal positivo con hasta tres decimales.");
    } else {
      const price = integer(weighted.unitPriceMinorPerUnit, "weightedSale.unitPriceMinorPerUnit", errors, 1);
      const expected = integer(weighted.expectedTotalMinor, "weightedSale.expectedTotalMinor", errors);
      if (price !== null && expected !== null) {
        const calculated = Number(roundDiv(BigInt(price) * BigInt(quantityMilli), 1000n));
        compare(expected, calculated, "weightedSale.expectedTotalMinor", errors);
      }
    }
  }

  const partialReturn = scenarios.partialReturn;
  if (!isRecord(partialReturn)) {
    errors.push("scenarios.partialReturn debe ser un objeto.");
  } else {
    const quantity = integer(partialReturn.quantityMilli, "partialReturn.quantityMilli", errors, 1);
    const refund = integer(partialReturn.expectedRefundMinor, "partialReturn.expectedRefundMinor", errors, 1);
    const cashAfterSale = integer(
      sale.expectedRegisterCashAfterSaleMinor,
      "mixedPaymentSale.expectedRegisterCashAfterSaleMinor",
      errors
    );
    const cashAfterRefund = integer(
      partialReturn.expectedRegisterCashAfterRefundMinor,
      "partialReturn.expectedRegisterCashAfterRefundMinor",
      errors
    );

    if (!soldBySku.has(partialReturn.sku)) errors.push("partialReturn.sku no aparece en la venta original.");
    if (quantity !== null && quantity > (soldBySku.get(partialReturn.sku) || 0)) {
      errors.push("partialReturn.quantityMilli supera la cantidad vendida.");
    }
    if (refund !== null && expectedTotal !== null && refund > expectedTotal) {
      errors.push("partialReturn.expectedRefundMinor supera el total de la venta.");
    }
    if (partialReturn.refundMethod === "cash" && cashAfterSale !== null && refund !== null && cashAfterRefund !== null) {
      compare(
        cashAfterRefund,
        cashAfterSale - refund,
        "partialReturn.expectedRegisterCashAfterRefundMinor",
        errors
      );
    }
  }

  const purchase = scenarios.purchaseReceiving;
  if (!isRecord(purchase)) {
    errors.push("scenarios.purchaseReceiving debe ser un objeto.");
  } else {
    const ordered = integer(purchase.orderedQuantityMilli, "purchaseReceiving.orderedQuantityMilli", errors, 1);
    const received = integer(purchase.receivedQuantityMilli, "purchaseReceiving.receivedQuantityMilli", errors, 1);
    const pending = integer(purchase.expectedPendingQuantityMilli, "purchaseReceiving.expectedPendingQuantityMilli", errors);
    if (ordered !== null && received !== null && pending !== null) {
      if (received > ordered) errors.push("purchaseReceiving.receivedQuantityMilli supera lo ordenado.");
      compare(pending, ordered - received, "purchaseReceiving.expectedPendingQuantityMilli", errors);
    }
    if (!catalogBySku.has(purchase.sku)) errors.push("purchaseReceiving.sku no existe en catalog.");
  }

  if (isRecord(scenarios.partialReturn) && isRecord(scenarios.purchaseReceiving)) {
    const expectedInventory = data.expectedInventory;
    if (!isRecord(expectedInventory)) {
      errors.push("expectedInventory debe ser un objeto.");
    } else {
      for (const [sku, soldQuantity] of soldBySku.entries()) {
        const item = catalogBySku.get(sku);
        const result = expectedInventory[sku];
        if (!item) {
          errors.push("No se puede calcular el stock: SKU no definido en catalog: " + sku + ".");
          continue;
        }
        if (!isRecord(result)) {
          errors.push("Falta expectedInventory para " + sku + ".");
          continue;
        }
        const opening = item.openingStockMilli;
        if (!Number.isSafeInteger(opening)) continue;
        const afterSale = opening - soldQuantity;
        const expectedAfterSale = integer(result.afterSaleMilli, "expectedInventory." + sku + ".afterSaleMilli", errors);
        if (expectedAfterSale !== null) compare(expectedAfterSale, afterSale, "expectedInventory." + sku + ".afterSaleMilli", errors);

        let afterReturn = afterSale;
        if (partialReturn.sku === sku && partialReturn.stockDisposition === "resalable") {
          const returned = integer(partialReturn.quantityMilli, "partialReturn.quantityMilli", errors);
          if (returned !== null) afterReturn += returned;
        }
        if (result.afterReturnMilli !== undefined) {
          const expectedAfterReturn = integer(result.afterReturnMilli, "expectedInventory." + sku + ".afterReturnMilli", errors);
          if (expectedAfterReturn !== null) compare(expectedAfterReturn, afterReturn, "expectedInventory." + sku + ".afterReturnMilli", errors);
        }

        if (purchase.sku === sku) {
          const received = integer(purchase.receivedQuantityMilli, "purchaseReceiving.receivedQuantityMilli", errors);
          if (received !== null) {
            const expectedAfterReceipt = integer(
              result.afterPartialReceiptMilli,
              "expectedInventory." + sku + ".afterPartialReceiptMilli",
              errors
            );
            if (expectedAfterReceipt !== null) compare(
              expectedAfterReceipt,
              afterReturn + received,
              "expectedInventory." + sku + ".afterPartialReceiptMilli",
              errors
            );
          }
        }
      }
    }
  }


  const checkout = scenarios.checkoutBeforePayment;
  if (!isRecord(checkout)) {
    errors.push("scenarios.checkoutBeforePayment debe ser un objeto.");
  } else {
    const sumCartLines = (lines, path) => {
      if (!Array.isArray(lines) || lines.length === 0) {
        errors.push(path + " debe contener al menos una línea.");
        return null;
      }
      let total = 0n;
      for (const [index, line] of lines.entries()) {
        const linePath = path + "[" + index + "]";
        if (!isRecord(line)) {
          errors.push(linePath + " debe ser un objeto.");
          continue;
        }
        if (!catalogBySku.has(line.sku)) errors.push(linePath + ".sku no existe en catalog.");
        const quantity = integer(line.quantityMilli, linePath + ".quantityMilli", errors, 1);
        const price = integer(line.unitPriceMinorPerUnit, linePath + ".unitPriceMinorPerUnit", errors, 1);
        const expected = integer(line.expectedLineTotalMinor, linePath + ".expectedLineTotalMinor", errors);
        if (quantity !== null && price !== null && expected !== null) {
          const calculated = Number(roundDiv(BigInt(quantity) * BigInt(price), 1000n));
          compare(expected, calculated, linePath + ".expectedLineTotalMinor", errors);
          total += BigInt(calculated);
        }
      }
      return Number(total);
    };

    const initialTotal = sumCartLines(checkout.initialLines, "checkoutBeforePayment.initialLines");
    const finalTotal = sumCartLines(checkout.finalLines, "checkoutBeforePayment.finalLines");
    const removedTotal = sumCartLines(
      (checkout.removedLines || []).map(line => ({
        sku: line.sku,
        quantityMilli: line.quantityMilli,
        unitPriceMinorPerUnit: line.unitPriceMinorPerUnit,
        expectedLineTotalMinor: line.expectedLineTotalMinor
      })),
      "checkoutBeforePayment.removedLines"
    );

    const expectedBefore = integer(checkout.expectedTotalBeforeRemovalMinor, "checkoutBeforePayment.expectedTotalBeforeRemovalMinor", errors);
    const expectedRemoved = integer(checkout.expectedRemovedTotalMinor, "checkoutBeforePayment.expectedRemovedTotalMinor", errors);
    const expectedAfter = integer(checkout.expectedTotalAfterRemovalMinor, "checkoutBeforePayment.expectedTotalAfterRemovalMinor", errors);

    if (initialTotal !== null && expectedBefore !== null) compare(expectedBefore, initialTotal, "checkoutBeforePayment.expectedTotalBeforeRemovalMinor", errors);
    if (removedTotal !== null && expectedRemoved !== null) compare(expectedRemoved, removedTotal, "checkoutBeforePayment.expectedRemovedTotalMinor", errors);
    if (finalTotal !== null && expectedAfter !== null) compare(expectedAfter, finalTotal, "checkoutBeforePayment.expectedTotalAfterRemovalMinor", errors);
    if (initialTotal !== null && removedTotal !== null && finalTotal !== null) {
      compare(initialTotal - removedTotal, finalTotal, "checkoutBeforePayment cart reconciliation", errors);
    }

    const finalSkus = new Set((checkout.finalLines || []).map(line => line?.sku));
    for (const [index, removed] of (checkout.removedLines || []).entries()) {
      if (finalSkus.has(removed.sku)) errors.push("checkoutBeforePayment.removedLines[" + index + "] sigue en el carrito final.");
    }

    for (const field of [
      "removedLineCreatesSaleLine",
      "removedLineCreatesStockMovement",
      "removedLineCreatesPayment",
      "removedLineCreatesFiscalDocument"
    ]) {
      compare(checkout[field], false, "checkoutBeforePayment." + field, errors);
    }

    const cash = checkout.cashTender;
    if (!isRecord(cash)) {
      errors.push("checkoutBeforePayment.cashTender debe ser un objeto.");
    } else {
      const tendered = integer(cash.tenderedMinor, "checkoutBeforePayment.cashTender.tenderedMinor", errors);
      const due = integer(cash.amountDueMinor, "checkoutBeforePayment.cashTender.amountDueMinor", errors);
      const change = integer(cash.expectedChangeMinor, "checkoutBeforePayment.cashTender.expectedChangeMinor", errors);
      const retained = integer(cash.expectedCashRetainedMinor, "checkoutBeforePayment.cashTender.expectedCashRetainedMinor", errors);
      if (tendered !== null && due !== null && change !== null && retained !== null) {
        if (tendered < due) errors.push("El efectivo de cashTender debe cubrir el importe asignado.");
        compare(change, Math.max(0, tendered - due), "checkoutBeforePayment.cashTender.expectedChangeMinor", errors);
        compare(retained, tendered - change, "checkoutBeforePayment.cashTender.expectedCashRetainedMinor", errors);
        compare(retained, due, "checkoutBeforePayment cash retained equals amount due", errors);
      }
    }

    const insufficient = checkout.insufficientCash;
    if (!isRecord(insufficient)) {
      errors.push("checkoutBeforePayment.insufficientCash debe ser un objeto.");
    } else {
      const tendered = integer(insufficient.tenderedMinor, "checkoutBeforePayment.insufficientCash.tenderedMinor", errors);
      const due = integer(insufficient.amountDueMinor, "checkoutBeforePayment.insufficientCash.amountDueMinor", errors);
      const shortfall = integer(insufficient.expectedShortfallMinor, "checkoutBeforePayment.insufficientCash.expectedShortfallMinor", errors);
      const change = integer(insufficient.expectedChangeMinor, "checkoutBeforePayment.insufficientCash.expectedChangeMinor", errors);
      if (tendered !== null && due !== null && shortfall !== null && change !== null) {
        if (tendered >= due) errors.push("insufficientCash debe ser menor al importe adeudado.");
        compare(shortfall, due - tendered, "checkoutBeforePayment.insufficientCash.expectedShortfallMinor", errors);
        compare(change, 0, "checkoutBeforePayment.insufficientCash.expectedChangeMinor", errors);
      }
      compare(insufficient.saleMayComplete, false, "checkoutBeforePayment.insufficientCash.saleMayComplete", errors);
    }
  }

  const terminal = scenarios.terminalPayment;
  if (!isRecord(terminal)) {
    errors.push("scenarios.terminalPayment debe ser un objeto.");
  } else {
    compare(terminal.currency, data.currency, "terminalPayment.currency", errors);
    const amount = integer(terminal.amountMinor, "terminalPayment.amountMinor", errors, 1);
    const checkoutDue = integer(scenarios.checkoutBeforePayment?.expectedTotalAfterRemovalMinor, "checkoutBeforePayment.expectedTotalAfterRemovalMinor", errors);
    if (amount !== null && checkoutDue !== null) compare(amount, checkoutDue, "terminalPayment.amountMinor", errors);
    if (typeof terminal.terminalId !== "string" || terminal.terminalId.trim() === "") errors.push("terminalPayment.terminalId es obligatorio.");
    if (typeof terminal.externalReference !== "string" || terminal.externalReference.trim() === "") errors.push("terminalPayment.externalReference es obligatorio.");
    if (typeof terminal.idempotencyKey !== "string" || terminal.idempotencyKey.trim() === "") errors.push("terminalPayment.idempotencyKey es obligatorio.");
    const expectedSequence = ["created", "at_terminal", "processed"];
    compare(JSON.stringify(terminal.statusSequence), JSON.stringify(expectedSequence), "terminalPayment.statusSequence", errors);
    compare(terminal.finalStatus, "processed", "terminalPayment.finalStatus", errors);
    compare(terminal.paidOnlyAfterFinalStatus, true, "terminalPayment.paidOnlyAfterFinalStatus", errors);
    compare(terminal.confirmedPaid, true, "terminalPayment.confirmedPaid", errors);
    compare(terminal.unknownStatusPolicy, "query-and-reconcile-before-any-new-emission", "terminalPayment.unknownStatusPolicy", errors);
    compare(terminal.terminalSlipIsFiscalDocument, false, "terminalPayment.terminalSlipIsFiscalDocument", errors);
    compare(terminal.itemizedReceiptOwner, "Rubrova", "terminalPayment.itemizedReceiptOwner", errors);
    const printRequirement = terminal.printRequirement;
    if (!isRecord(printRequirement)) {
      errors.push("terminalPayment.printRequirement debe ser un objeto.");
    } else {
      compare(
        printRequirement.itemizedReceiptMustPrintFromTerminal,
        true,
        "terminalPayment.printRequirement.itemizedReceiptMustPrintFromTerminal",
        errors
      );
      compare(
        printRequirement.expectedPrintAfterStatus,
        "processed",
        "terminalPayment.printRequirement.expectedPrintAfterStatus",
        errors
      );
      compare(
        printRequirement.contentOwner,
        "Rubrova",
        "terminalPayment.printRequirement.contentOwner",
        errors
      );
      compare(
        printRequirement.terminalPrintIsFiscalDocument,
        false,
        "terminalPayment.printRequirement.terminalPrintIsFiscalDocument",
        errors
      );
      const requiredContents = new Set(printRequirement.requiredContents || []);
      for (const content of ["items", "quantities", "unit-prices", "discounts", "total", "payment-reference"]) {
        if (!requiredContents.has(content)) {
          errors.push("Falta contenido obligatorio de impresión desde terminal: " + content + ".");
        }
      }
    }
  }


  const businessUnits = data.businessUnits;
  if (!Array.isArray(businessUnits) || businessUnits.length < 3) {
    errors.push("businessUnits debe contener al menos tres unidades.");
  }
  const unitCodes = new Set((businessUnits || []).map(unit => unit?.code).filter(Boolean));
  for (const required of ["BU-RETAIL","BU-WHOLESALE","BU-SERVICES"]) {
    if (!unitCodes.has(required)) errors.push("Falta la unidad de negocio " + required + ".");
  }
  if (unitCodes.size !== (businessUnits || []).length) errors.push("businessUnits tiene códigos vacíos o duplicados.");

  const multiArea = scenarios.multiAreaAllocation;
  if (!isRecord(multiArea)) {
    errors.push("scenarios.multiAreaAllocation debe ser un objeto.");
  } else {
    compare(multiArea.expectedCustomerAccountCount, 1, "multiAreaAllocation.expectedCustomerAccountCount", errors);
    compare(multiArea.sameCustomerAcrossBusinessUnits, true, "multiAreaAllocation.sameCustomerAcrossBusinessUnits", errors);
    compare(multiArea.channelsAreNotBusinessUnits, true, "multiAreaAllocation.channelsAreNotBusinessUnits", errors);
    if (multiArea.sharedCustomerCode !== data.businessCustomers?.[0]?.code) errors.push("multiAreaAllocation debe usar la cuenta empresarial compartida.");
    let total = 0;
    const seenUnits = new Set();
    for (const [index, tx] of (multiArea.businessUnitTransactions || []).entries()) {
      const path = "multiAreaAllocation.businessUnitTransactions[" + index + "]";
      if (!isRecord(tx)) { errors.push(path + " debe ser un objeto."); continue; }
      if (seenUnits.has(tx.businessUnit)) errors.push(path + " repite una unidad.");
      seenUnits.add(tx.businessUnit);
      const amount = integer(tx.amountMinor, path + ".amountMinor", errors, 1);
      if (amount !== null) total += amount;
      if (!unitCodes.has(tx.businessUnit)) errors.push(path + ".businessUnit no existe.");
      if (typeof tx.channel !== "string" || !tx.channel) errors.push(path + ".channel es obligatorio.");
    }
    const expected = integer(multiArea.expectedConsolidatedRevenueMinor, "multiAreaAllocation.expectedConsolidatedRevenueMinor", errors);
    if (expected !== null) compare(total, expected, "multiAreaAllocation.expectedConsolidatedRevenueMinor", errors);
  }

  const wholesale = scenarios.wholesaleOrder;
  if (!isRecord(wholesale) || !Array.isArray(wholesale.lines) || wholesale.lines.length === 0) {
    errors.push("scenarios.wholesaleOrder debe contener líneas.");
  } else {
    if (wholesale.businessUnit !== "BU-WHOLESALE") errors.push("wholesaleOrder debe pertenecer a BU-WHOLESALE.");
    if (wholesale.customerCode !== data.businessCustomers?.[0]?.code) errors.push("wholesaleOrder debe usar la cuenta empresarial compartida.");
    let total = 0n;
    for (const [index, line] of wholesale.lines.entries()) {
      const path = "wholesaleOrder.lines[" + index + "]";
      if (!isRecord(line)) { errors.push(path + " debe ser un objeto."); continue; }
      if (!catalogBySku.has(line.sku)) errors.push(path + ".sku no existe en catalog.");
      const quantity = integer(line.quantityMilli, path + ".quantityMilli", errors, 1);
      const minQty = integer(line.minQuantityMilli, path + ".minQuantityMilli", errors, 1);
      const multiple = integer(line.packMultipleMilli, path + ".packMultipleMilli", errors, 1);
      const tierQty = integer(line.priceTierMinQuantityMilli, path + ".priceTierMinQuantityMilli", errors, 1);
      const price = integer(line.unitPriceMinor, path + ".unitPriceMinor", errors, 1);
      const expectedLine = integer(line.expectedLineTotalMinor, path + ".expectedLineTotalMinor", errors, 1);
      if (quantity !== null && minQty !== null && quantity < minQty) errors.push(path + " no cumple el mínimo por SKU.");
      if (quantity !== null && multiple !== null && quantity % multiple !== 0) errors.push(path + " no respeta el múltiplo de empaque.");
      if (quantity !== null && tierQty !== null && quantity < tierQty) errors.push(path + " no alcanza el umbral de precio aplicado.");
      if (quantity !== null && price !== null && expectedLine !== null) {
        const calculated = Number(roundDiv(BigInt(quantity) * BigInt(price), 1000n));
        compare(expectedLine, calculated, path + ".expectedLineTotalMinor", errors);
        total += BigInt(calculated);
      }
    }
    const minOrder = integer(wholesale.minimumOrderValueMinor, "wholesaleOrder.minimumOrderValueMinor", errors, 1);
    const expectedTotal = integer(wholesale.expectedTotalMinor, "wholesaleOrder.expectedTotalMinor", errors, 1);
    if (expectedTotal !== null) compare(Number(total), expectedTotal, "wholesaleOrder.expectedTotalMinor", errors);
    if (minOrder !== null && expectedTotal !== null && expectedTotal < minOrder) errors.push("wholesaleOrder no alcanza el importe mínimo.");
    const credit = wholesale.credit;
    if (!isRecord(credit)) {
      errors.push("wholesaleOrder.credit debe estar definido.");
    } else {
      const limit = integer(credit.creditLimitMinor, "wholesaleOrder.credit.creditLimitMinor", errors, 1);
      const before = integer(credit.openExposureBeforeMinor, "wholesaleOrder.credit.openExposureBeforeMinor", errors);
      const after = integer(credit.expectedExposureAfterMinor, "wholesaleOrder.credit.expectedExposureAfterMinor", errors);
      if (before !== null && expectedTotal !== null && after !== null) compare(after, before + expectedTotal, "wholesaleOrder.credit.expectedExposureAfterMinor", errors);
      if (limit !== null && after !== null && after > limit && credit.approved !== true) errors.push("La exposición de crédito excede el límite sin autorización.");
    }
  }

  const shipmentScenario = scenarios.shipmentAfterSale;
  if (!isRecord(shipmentScenario) || !Array.isArray(shipmentScenario.shipments)) {
    errors.push("scenarios.shipmentAfterSale debe contener envíos.");
  } else {
    compare(shipmentScenario.trackingReferenceAtSale, null, "shipmentAfterSale.trackingReferenceAtSale", errors);
    compare(shipmentScenario.saleRequiresTracking, false, "shipmentAfterSale.saleRequiresTracking", errors);
    const saleDate = Date.parse(shipmentScenario.saleConfirmedAt);
    if (!Number.isFinite(saleDate)) errors.push("shipmentAfterSale.saleConfirmedAt debe ser una fecha ISO válida.");
    const shipmentIds = new Set();
    const shipped = new Map();
    for (const [index, shipment] of shipmentScenario.shipments.entries()) {
      const path = "shipmentAfterSale.shipments[" + index + "]";
      if (!isRecord(shipment)) { errors.push(path + " debe ser un objeto."); continue; }
      if (shipmentIds.has(shipment.shipmentId)) errors.push("shipmentId duplicado: " + shipment.shipmentId);
      shipmentIds.add(shipment.shipmentId);
      const createdAt = Date.parse(shipment.createdAt);
      if (!Number.isFinite(createdAt) || (Number.isFinite(saleDate) && createdAt <= saleDate)) errors.push(path + " debe crearse después de la venta.");
      if (!["carrier-handoff","customer-pickup","own-fleet"].includes(shipment.mode)) errors.push(path + ".mode no es válido.");
      if (shipment.mode === "carrier-handoff") {
        if (!shipment.carrierCode) errors.push(path + " requiere carrierCode.");
        if (!shipment.trackingReference) errors.push(path + " requiere trackingReference para el handoff del caso.");
        const trackedAt = Date.parse(shipment.trackingAssignedAt);
        if (!Number.isFinite(trackedAt) || (Number.isFinite(saleDate) && trackedAt <= saleDate)) errors.push(path + " debe asignar tracking después de la venta.");
      }
      for (const line of shipment.lines || []) {
        if (!isRecord(line)) continue;
        const qty = integer(line.quantityMilli, path + ".lines.quantityMilli", errors, 1);
        if (qty !== null) shipped.set(line.sku, (shipped.get(line.sku) || 0) + qty);
      }
    }
    const expected = shipmentScenario.expectedShippedQuantitiesMilli || {};
    for (const [sku, quantity] of Object.entries(expected)) {
      const qty = integer(quantity, "shipmentAfterSale.expectedShippedQuantitiesMilli." + sku, errors);
      if (qty !== null) compare(shipped.get(sku) || 0, qty, "shipmentAfterSale.shipped." + sku, errors);
    }
    for (const sku of shipped.keys()) if (!(sku in expected)) errors.push("Se despachó SKU no incluido en el pedido: " + sku + ".");
  }

  const service = scenarios.b2bServiceContract;
  if (!isRecord(service)) {
    errors.push("scenarios.b2bServiceContract debe ser un objeto.");
  } else {
    if (service.businessUnit !== "BU-SERVICES") errors.push("b2bServiceContract debe pertenecer a BU-SERVICES.");
    if (service.customerCode !== data.businessCustomers?.[0]?.code) errors.push("b2bServiceContract debe usar la cuenta empresarial compartida.");
    const start = Date.parse(service.startsOn);
    const end = Date.parse(service.endsOn);
    if (!Number.isFinite(start) || !Number.isFinite(end) || start >= end) errors.push("El período del contrato B2B no es válido.");
    const wo = service.workOrder;
    if (!isRecord(wo)) errors.push("b2bServiceContract.workOrder debe existir.");
    else {
      const labor = integer(wo.laborCostMinor, "b2bServiceContract.workOrder.laborCostMinor", errors);
      const materials = integer(wo.materialsCostMinor, "b2bServiceContract.workOrder.materialsCostMinor", errors);
      const travel = integer(wo.travelCostMinor, "b2bServiceContract.workOrder.travelCostMinor", errors);
      const expectedCost = integer(service.expectedDirectCostMinor, "b2bServiceContract.expectedDirectCostMinor", errors);
      const fee = integer(service.monthlyFeeMinor, "b2bServiceContract.monthlyFeeMinor", errors, 1);
      const expectedContribution = integer(service.expectedContributionMinor, "b2bServiceContract.expectedContributionMinor", errors);
      if (labor !== null && materials !== null && travel !== null && expectedCost !== null) compare(expectedCost, labor + materials + travel, "b2bServiceContract.expectedDirectCostMinor", errors);
      if (fee !== null && expectedCost !== null && expectedContribution !== null) compare(expectedContribution, fee - expectedCost, "b2bServiceContract.expectedContributionMinor", errors);
      if (!Number.isInteger(wo.evidenceCount) || wo.evidenceCount < 1) errors.push("La orden de trabajo debe contener evidencia.");
      compare(wo.customerAcceptanceRequired, true, "b2bServiceContract.workOrder.customerAcceptanceRequired", errors);
    }
    compare(service.duplicateInvoiceCount, 0, "b2bServiceContract.duplicateInvoiceCount", errors);
  }

  const profitability = scenarios.businessUnitProfitability;
  if (!isRecord(profitability) || !Array.isArray(profitability.businessUnits)) {
    errors.push("scenarios.businessUnitProfitability debe contener áreas.");
  } else {
    const totals = {netRevenueMinor:0,goodsOrServiceCostMinor:0,variableServingCostMinor:0,directFixedCostMinor:0,sharedCostAllocationMinor:0,operatingResultMinor:0};
    let allocatedShared = 0;
    const seen = new Set();
    for (const [index, unit] of profitability.businessUnits.entries()) {
      const path = "businessUnitProfitability.businessUnits[" + index + "]";
      if (!isRecord(unit)) { errors.push(path + " debe ser un objeto."); continue; }
      if (seen.has(unit.businessUnit)) errors.push(path + " duplica una unidad.");
      seen.add(unit.businessUnit);
      const revenue = integer(unit.netRevenueMinor, path + ".netRevenueMinor", errors);
      const goods = integer(unit.goodsOrServiceCostMinor, path + ".goodsOrServiceCostMinor", errors);
      const variable = integer(unit.variableServingCostMinor, path + ".variableServingCostMinor", errors);
      const fixed = integer(unit.directFixedCostMinor, path + ".directFixedCostMinor", errors);
      const shared = integer(unit.sharedCostAllocationMinor, path + ".sharedCostAllocationMinor", errors);
      const result = integer(unit.expectedOperatingResultMinor, path + ".expectedOperatingResultMinor", errors);
      if ([revenue,goods,variable,fixed,shared,result].every(v => v !== null)) {
        compare(result, revenue - goods - variable - fixed - shared, path + ".expectedOperatingResultMinor", errors);
        totals.netRevenueMinor += revenue; totals.goodsOrServiceCostMinor += goods; totals.variableServingCostMinor += variable;
        totals.directFixedCostMinor += fixed; totals.sharedCostAllocationMinor += shared; totals.operatingResultMinor += result;
        allocatedShared += shared;
      }
    }
    const sharedPool = integer(profitability.sharedCostPoolMinor, "businessUnitProfitability.sharedCostPoolMinor", errors);
    const unallocated = integer(profitability.unallocatedSharedCostMinor, "businessUnitProfitability.unallocatedSharedCostMinor", errors);
    if (sharedPool !== null && unallocated !== null) compare(allocatedShared + unallocated, sharedPool, "businessUnitProfitability shared allocation reconciliation", errors);
    const consolidated = profitability.expectedConsolidated;
    if (!isRecord(consolidated)) errors.push("businessUnitProfitability.expectedConsolidated debe existir.");
    else for (const key of Object.keys(totals)) {
      const expected = integer(consolidated[key], "businessUnitProfitability.expectedConsolidated." + key, errors);
      if (expected !== null) compare(totals[key], expected, "businessUnitProfitability.expectedConsolidated." + key, errors);
    }
  }


  const internalTransfer = scenarios.internalBusinessUnitTransfer;
  if (!isRecord(internalTransfer)) {
    errors.push("scenarios.internalBusinessUnitTransfer debe existir.");
  } else {
    compare(internalTransfer.sameLegalEntity, true, "internalBusinessUnitTransfer.sameLegalEntity", errors);
    if (internalTransfer.sourceBusinessUnit === internalTransfer.destinationBusinessUnit) {
      errors.push("La transferencia interna debe conectar dos unidades distintas.");
    }
    if (!unitCodes.has(internalTransfer.sourceBusinessUnit)) errors.push("La unidad de origen de transferencia interna no existe.");
    if (!unitCodes.has(internalTransfer.destinationBusinessUnit)) errors.push("La unidad de destino de transferencia interna no existe.");
    if (!catalogBySku.has(internalTransfer.sku)) errors.push("El SKU de transferencia interna no existe.");
    integer(internalTransfer.quantityMilli, "internalBusinessUnitTransfer.quantityMilli", errors, 1);
    const physicalCount = integer(internalTransfer.physicalInventoryMovementCount, "internalBusinessUnitTransfer.physicalInventoryMovementCount", errors, 1);
    compare(physicalCount, 1, "internalBusinessUnitTransfer.physicalInventoryMovementCount", errors);
    const carryingCost = integer(internalTransfer.actualCarryingCostMinor, "internalBusinessUnitTransfer.actualCarryingCostMinor", errors, 1);
    const transferPrice = integer(internalTransfer.managerialTransferPriceMinor, "internalBusinessUnitTransfer.managerialTransferPriceMinor", errors, 1);
    const internalRevenue = integer(internalTransfer.internalManagerialRevenueMinor, "internalBusinessUnitTransfer.internalManagerialRevenueMinor", errors);
    const internalCost = integer(internalTransfer.internalManagerialCostMinor, "internalBusinessUnitTransfer.internalManagerialCostMinor", errors);
    const elimination = integer(internalTransfer.expectedConsolidationEliminationMinor, "internalBusinessUnitTransfer.expectedConsolidationEliminationMinor", errors);
    const revenueImpact = integer(internalTransfer.expectedConsolidatedExternalRevenueImpactMinor, "internalBusinessUnitTransfer.expectedConsolidatedExternalRevenueImpactMinor", errors);
    const consolidatedCost = integer(internalTransfer.expectedConsolidatedCostMinor, "internalBusinessUnitTransfer.expectedConsolidatedCostMinor", errors);
    if (transferPrice !== null && internalRevenue !== null) compare(internalRevenue, transferPrice, "internalBusinessUnitTransfer.internalManagerialRevenueMinor", errors);
    if (transferPrice !== null && internalCost !== null) compare(internalCost, transferPrice, "internalBusinessUnitTransfer.internalManagerialCostMinor", errors);
    if (transferPrice !== null && elimination !== null) compare(elimination, transferPrice, "internalBusinessUnitTransfer.expectedConsolidationEliminationMinor", errors);
    if (revenueImpact !== null) compare(revenueImpact, 0, "internalBusinessUnitTransfer.expectedConsolidatedExternalRevenueImpactMinor", errors);
    if (carryingCost !== null && consolidatedCost !== null) compare(consolidatedCost, carryingCost, "internalBusinessUnitTransfer.expectedConsolidatedCostMinor", errors);
    for (const field of ["createsExternalSale","createsFiscalInvoice","createsCustomerReceivable","createsExternalCashMovement"]) {
      compare(internalTransfer[field], false, "internalBusinessUnitTransfer." + field, errors);
    }
  }


  const commercial = scenarios.commercialIntelligence;
  if (!isRecord(commercial)) {
    errors.push("scenarios.commercialIntelligence debe existir.");
  } else {
    const allowedSegments = new Set(["first-brand", "second-brand", "economy", "own-brand", "alternative", "generic"]);
    const brandBySku = new Map();
    const categorySegments = new Map();

    if (!Array.isArray(commercial.brandProducts) || commercial.brandProducts.length < 2) {
      errors.push("commercialIntelligence.brandProducts debe contener al menos dos marcas comparables.");
    } else {
      for (const [index, product] of commercial.brandProducts.entries()) {
        const path = "commercialIntelligence.brandProducts[" + index + "]";
        if (!isRecord(product)) { errors.push(path + " debe ser un objeto."); continue; }
        if (!catalogBySku.has(product.sku)) errors.push(path + ".sku no existe en catalog.");
        if (brandBySku.has(product.sku)) errors.push(path + " duplica el SKU.");
        brandBySku.set(product.sku, product);
        if (typeof product.categoryCode !== "string" || !product.categoryCode) errors.push(path + ".categoryCode es obligatorio.");
        if (typeof product.brandCode !== "string" || !product.brandCode) errors.push(path + ".brandCode es obligatorio.");
        if (typeof product.brandName !== "string" || !product.brandName) errors.push(path + ".brandName es obligatorio.");
        if (!allowedSegments.has(product.segment)) errors.push(path + ".segment no es un segmento comercial permitido.");
        if (typeof product.segmentEffectiveFrom !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(product.segmentEffectiveFrom) || !Number.isFinite(Date.parse(product.segmentEffectiveFrom + "T00:00:00Z"))) {
          errors.push(path + ".segmentEffectiveFrom debe ser una fecha ISO válida.");
        }
        if (product.baseUnit !== "g") errors.push(path + ".baseUnit debe ser g en este fixture comparable por kilogramo.");
        const content = integer(product.packageContentBaseMilli, path + ".packageContentBaseMilli", errors, 1);
        const price = integer(product.packagePriceMinor, path + ".packagePriceMinor", errors, 1);
        const expectedComparable = integer(product.expectedComparablePricePerKgMinor, path + ".expectedComparablePricePerKgMinor", errors, 1);
        if (content !== null && price !== null && expectedComparable !== null) {
          const calculated = Number(roundDiv(BigInt(price) * 1000000n, BigInt(content)));
          compare(expectedComparable, calculated, path + ".expectedComparablePricePerKgMinor", errors);
        }
        if (typeof product.categoryCode === "string") {
          if (!categorySegments.has(product.categoryCode)) categorySegments.set(product.categoryCode, new Set());
          categorySegments.get(product.categoryCode).add(product.segment);
        }
      }
      for (const [category, segments] of categorySegments) {
        if (!segments.has("first-brand") || !segments.has("second-brand")) {
          errors.push("La categoría " + category + " debe permitir comparar primera y segunda marca.");
        }
      }
    }

    const periods = commercial.brandSalesPeriods;
    if (!Array.isArray(periods) || periods.length === 0) {
      errors.push("commercialIntelligence.brandSalesPeriods debe contener períodos.");
    } else {
      const seenPeriods = new Set();
      for (const [periodIndex, period] of periods.entries()) {
        const periodPath = "commercialIntelligence.brandSalesPeriods[" + periodIndex + "]";
        if (!isRecord(period)) { errors.push(periodPath + " debe ser un objeto."); continue; }
        if (!["calendar-quarter", "southern-season"].includes(period.periodType)) {
          errors.push(periodPath + ".periodType debe distinguir trimestre calendario de estación del hemisferio sur.");
        }
        if (typeof period.periodKey !== "string" || !period.periodKey) errors.push(periodPath + ".periodKey es obligatorio.");
        const periodIdentity = period.periodType + ":" + period.periodKey;
        if (seenPeriods.has(periodIdentity)) errors.push(periodPath + " duplica el período.");
        seenPeriods.add(periodIdentity);
        const days = integer(period.observationDays, periodPath + ".observationDays", errors, 1);
        const sales = period.sales;
        if (!Array.isArray(sales) || sales.length !== brandBySku.size) {
          errors.push(periodPath + ".sales debe contener una fila para cada producto de marca.");
          continue;
        }
        const seenSkus = new Set();
        let fullAvailability = true;
        for (const [rowIndex, row] of sales.entries()) {
          const rowPath = periodPath + ".sales[" + rowIndex + "]";
          if (!isRecord(row)) { errors.push(rowPath + " debe ser un objeto."); continue; }
          const product = brandBySku.get(row.sku);
          if (!product) { errors.push(rowPath + ".sku no está definido en brandProducts."); continue; }
          if (seenSkus.has(row.sku)) errors.push(rowPath + " repite un SKU en el período.");
          seenSkus.add(row.sku);
          const packages = integer(row.soldPackages, rowPath + ".soldPackages", errors);
          const averagePrice = integer(row.averageSellingPriceMinor, rowPath + ".averageSellingPriceMinor", errors, 1);
          const revenue = integer(row.netRevenueMinor, rowPath + ".netRevenueMinor", errors);
          const quantity = integer(row.baseQuantityMilli, rowPath + ".baseQuantityMilli", errors);
          const available = integer(row.availableDays, rowPath + ".availableDays", errors);
          const stockout = integer(row.stockoutDays, rowPath + ".stockoutDays", errors);
          const promotions = integer(row.promotionDays, rowPath + ".promotionDays", errors);
          if (days !== null && available !== null && stockout !== null) {
            if (available > days || stockout > days || available + stockout !== days) errors.push(rowPath + " debe conciliar días disponibles y días sin stock con observationDays.");
            if (available < days) fullAvailability = false;
          }
          if (days !== null && promotions !== null && promotions > days) errors.push(rowPath + ".promotionDays no puede superar observationDays.");
          if (packages !== null && averagePrice !== null && revenue !== null) {
            compare(revenue, packages * averagePrice, rowPath + ".netRevenueMinor", errors);
          }
          if (packages !== null && product.packageContentBaseMilli !== undefined && quantity !== null) {
            compare(quantity, packages * product.packageContentBaseMilli, rowPath + ".baseQuantityMilli", errors);
          }
        }
        for (const sku of brandBySku.keys()) if (!seenSkus.has(sku)) errors.push(periodPath + " omite el SKU " + sku + ".");
        compare(period.preferenceConclusionAllowed, fullAvailability, periodPath + ".preferenceConclusionAllowed", errors);
      }
      const quarterKeys = new Set(periods.filter(p => p?.periodType === "calendar-quarter").map(p => p.periodKey));
      const seasonKeys = new Set(periods.filter(p => p?.periodType === "southern-season").map(p => p.periodKey));
      if (quarterKeys.size === 0 || seasonKeys.size === 0) errors.push("La serie debe mantener períodos trimestrales y estaciones del hemisferio sur por separado.");
      for (const key of quarterKeys) if (seasonKeys.has(key)) errors.push("Un mismo período no puede clasificarse como trimestre y estación: " + key + ".");
    }
    
    const costing = commercial.costing;
    if (!isRecord(costing)) {
      errors.push("commercialIntelligence.costing debe existir.");
    } else {
      compare(costing.method, "FIFO", "commercialIntelligence.costing.method", errors);
      const receipts = costing.receipts;
      if (!Array.isArray(receipts) || receipts.length === 0) {
        errors.push("commercialIntelligence.costing.receipts debe contener capas de costo.");
      } else {
        let previousDate = "";
        let totalReceived = 0;
        const layers = [];
        for (const [index, receipt] of receipts.entries()) {
          const path = "commercialIntelligence.costing.receipts[" + index + "]";
          if (!isRecord(receipt)) { errors.push(path + " debe ser un objeto."); continue; }
          if (typeof receipt.receiptDate !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(receipt.receiptDate) || (previousDate && receipt.receiptDate <= previousDate)) {
            errors.push(path + ".receiptDate debe ser ISO y estar ordenada cronológicamente.");
          }
          previousDate = receipt.receiptDate || previousDate;
          const quantity = integer(receipt.quantityMilli, path + ".quantityMilli", errors, 1);
          const unitCost = integer(receipt.unitCostMinor, path + ".unitCostMinor", errors, 1);
          if (quantity !== null && unitCost !== null) {
            totalReceived += quantity;
            layers.push({remaining: quantity, unitCost});
          }
        }
        const issued = integer(costing.issuedQuantityMilli, "commercialIntelligence.costing.issuedQuantityMilli", errors, 1);
        const expectedCogs = integer(costing.expectedCogsMinor, "commercialIntelligence.costing.expectedCogsMinor", errors);
        const expectedEndingQty = integer(costing.expectedEndingQuantityMilli, "commercialIntelligence.costing.expectedEndingQuantityMilli", errors);
        const expectedEndingValue = integer(costing.expectedEndingInventoryValueMinor, "commercialIntelligence.costing.expectedEndingInventoryValueMinor", errors);
        if (issued !== null) {
          if (issued > totalReceived) errors.push("commercialIntelligence.costing.issuedQuantityMilli supera las recepciones.");
          let remainingToIssue = issued;
          let cogs = 0n;
          let endingValue = 0n;
          let endingQty = 0;
          for (const layer of layers) {
            const consumed = Math.min(layer.remaining, remainingToIssue);
            if (consumed > 0) {
              cogs += roundDiv(BigInt(consumed) * BigInt(layer.unitCost), 1000n);
              remainingToIssue -= consumed;
            }
            const remaining = layer.remaining - consumed;
            endingQty += remaining;
            endingValue += roundDiv(BigInt(remaining) * BigInt(layer.unitCost), 1000n);
          }
          if (expectedCogs !== null) compare(expectedCogs, Number(cogs), "commercialIntelligence.costing.expectedCogsMinor", errors);
          if (expectedEndingQty !== null) compare(expectedEndingQty, endingQty, "commercialIntelligence.costing.expectedEndingQuantityMilli", errors);
          if (expectedEndingValue !== null) compare(expectedEndingValue, Number(endingValue), "commercialIntelligence.costing.expectedEndingInventoryValueMinor", errors);
        }
      }
      const revenue = integer(costing.netRevenueMinor, "commercialIntelligence.costing.netRevenueMinor", errors);
      const cogs = integer(costing.expectedCogsMinor, "commercialIntelligence.costing.expectedCogsMinor", errors);
      const variable = integer(costing.variableCostsMinor, "commercialIntelligence.costing.variableCostsMinor", errors);
      const gross = integer(costing.expectedGrossProfitMinor, "commercialIntelligence.costing.expectedGrossProfitMinor", errors);
      const contribution = integer(costing.expectedContributionMinor, "commercialIntelligence.costing.expectedContributionMinor", errors);
      const replacementCost = integer(costing.replacementUnitCostMinor, "commercialIntelligence.costing.replacementUnitCostMinor", errors, 1);
      const issued = integer(costing.issuedQuantityMilli, "commercialIntelligence.costing.issuedQuantityMilli", errors, 1);
      const replacementGross = integer(costing.expectedReplacementGrossProfitMinor, "commercialIntelligence.costing.expectedReplacementGrossProfitMinor", errors);
      const replacementContribution = integer(costing.expectedReplacementContributionMinor, "commercialIntelligence.costing.expectedReplacementContributionMinor", errors);
      if (revenue !== null && cogs !== null && gross !== null) compare(gross, revenue - cogs, "commercialIntelligence.costing.expectedGrossProfitMinor", errors);
      if (gross !== null && variable !== null && contribution !== null) compare(contribution, gross - variable, "commercialIntelligence.costing.expectedContributionMinor", errors);
      if (revenue !== null && replacementCost !== null && issued !== null && replacementGross !== null) {
        const replacementCogs = Number(roundDiv(BigInt(issued) * BigInt(replacementCost), 1000n));
        compare(replacementGross, revenue - replacementCogs, "commercialIntelligence.costing.expectedReplacementGrossProfitMinor", errors);
      }
      if (replacementGross !== null && variable !== null && replacementContribution !== null) {
        compare(replacementContribution, replacementGross - variable, "commercialIntelligence.costing.expectedReplacementContributionMinor", errors);
      }
    }
  }

  const resilience = data.resilience;
  if (!isRecord(resilience)) {
    errors.push("resilience debe ser un objeto.");
  } else {
    const repeats = integer(resilience.repeatSubmissionCount, "resilience.repeatSubmissionCount", errors, 2);
    if (repeats !== null && repeats < 3) errors.push("La prueba común requiere al menos tres reintentos.");
    const required = new Set(resilience.requiredOutcomes || []);
    for (const outcome of [
      "one-sale-record",
      "one-cash-payment",
      "one-transfer-payment",
      "one-stock-decrement-per-sold-line",
      "no-data-loss-after-forced-close",
      "backup-restores-consistent-ledger"
    ]) {
      if (!required.has(outcome)) errors.push("Falta el resultado de resiliencia obligatorio: " + outcome + ".");
    }
  }

  const fiscal = data.fiscal;
  if (!isRecord(fiscal)) {
    errors.push("fiscal debe ser un objeto.");
  } else {
    compare(fiscal.environment, "homologation-only", "fiscal.environment", errors);
    compare(fiscal.productionCredentialsAllowed, false, "fiscal.productionCredentialsAllowed", errors);
    compare(fiscal.realCustomerDataAllowed, false, "fiscal.realCustomerDataAllowed", errors);
    compare(
      fiscal.retryAfterUnknownResult,
      "query-and-reconcile-before-any-new-emission",
      "fiscal.retryAfterUnknownResult",
      errors
    );
  }

  return {
    valid: errors.length === 0,
    errors,
    summary: {
      articleCount: data.catalog.length,
      mixedPaymentLines: sale.lines.length,
      scenarioCount: Object.keys(scenarios).length,
      currency: data.currency,
      locale: data.locale
    }
  };
}

export function readFixture(path = defaultFixturePath) {
  return JSON.parse(readFileSync(path, "utf8"));
}
