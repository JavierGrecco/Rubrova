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
