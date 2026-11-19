import assert from "node:assert/strict";
import { test } from "node:test";
import { readFixture, validateFixture } from "./fixture-validator.mjs";

test("el dataset canónico cumple sus invariantes", () => {
  const result = validateFixture(readFixture());
  assert.equal(result.valid, true, result.errors.join("\n"));
  assert.equal(result.summary.currency, "ARS");
  assert.equal(result.summary.articleCount, 3);
});

test("rechaza un total de línea incorrecto", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.mixedPaymentSale.lines[0].expectedLineTotalMinor += 1;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("expectedLineTotalMinor")));
});

test("rechaza pagos que no concilian con la venta", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.mixedPaymentSale.payments[0].amountMinor += 1;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("payments total")));
});

test("rechaza una existencia posterior a la venta que no coincide", () => {
  const fixture = structuredClone(readFixture());
  fixture.expectedInventory["SKU-UNIT-001"].afterSaleMilli += 1;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("afterSaleMilli")));
});

test("rechaza fiscalidad de prueba configurada para producción", () => {
  const fixture = structuredClone(readFixture());
  fixture.fiscal.productionCredentialsAllowed = true;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("productionCredentialsAllowed")));
});

test("rechaza artículos duplicados y barras repetidas", () => {
  const fixture = structuredClone(readFixture());
  fixture.catalog[1].sku = fixture.catalog[0].sku;
  fixture.catalog[1].barcode = fixture.catalog[0].barcode;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("SKU duplicado")));
  assert.ok(result.errors.some(message => message.includes("Código de barras duplicado")));
});


test("el retiro de una línea antes del pago reconcilia el carrito sin crear movimientos", () => {
  const result = validateFixture(readFixture());
  assert.equal(result.valid, true, result.errors.join("\\n"));
  const fixture = readFixture();
  const checkout = fixture.scenarios.checkoutBeforePayment;
  assert.equal(checkout.expectedTotalBeforeRemovalMinor, 1635000);
  assert.equal(checkout.expectedTotalAfterRemovalMinor, 1135000);
  assert.equal(checkout.removedLineCreatesStockMovement, false);
});

test("rechaza vuelto incorrecto", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.checkoutBeforePayment.cashTender.expectedChangeMinor += 1;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("cashTender.expectedChangeMinor")));
});

test("rechaza un artículo que se quitó pero sigue en el carrito final", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.checkoutBeforePayment.finalLines.push({
    sku: "SKU-VAR-001",
    quantityMilli: 1000,
    unitPriceMinorPerUnit: 500000,
    expectedLineTotalMinor: 500000
  });
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("sigue en el carrito final")));
});

test("rechaza una secuencia terminal que marca el pago antes de procesarlo", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.terminalPayment.statusSequence = ["created", "processed"];
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("terminalPayment.statusSequence")));
});

test("rechaza un importe terminal diferente del total final del checkout", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.terminalPayment.amountMinor += 100;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("terminalPayment.amountMinor")));
});


test("exige impresión del ticket detallado desde la terminal", () => {
  const result = validateFixture(readFixture());
  assert.equal(result.valid, true, result.errors.join("\\n"));
  const fixture = readFixture();
  assert.equal(
    fixture.scenarios.terminalPayment.printRequirement.itemizedReceiptMustPrintFromTerminal,
    true
  );
});

test("rechaza una terminal que solo devuelve el voucher sin imprimir el ticket de Rubrova", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.terminalPayment.printRequirement.itemizedReceiptMustPrintFromTerminal = false;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("itemizedReceiptMustPrintFromTerminal")));
});


test("valida áreas, mayorista, despacho posterior, servicios y rentabilidad consolidada", () => {
  const result = validateFixture(readFixture());
  assert.equal(result.valid, true, result.errors.join("\\n"));
});

test("rechaza un mínimo de compra mayorista incumplido", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.wholesaleOrder.lines[0].quantityMilli = 6000;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("mínimo por SKU")));
});

test("rechaza tracking exigido al momento de la venta", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.shipmentAfterSale.trackingReferenceAtSale = "GUIA-DEMASIADO-PRONTO";
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("trackingReferenceAtSale")));
});

test("rechaza rentabilidad consolidada que no coincide con las áreas", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.businessUnitProfitability.expectedConsolidated.operatingResultMinor += 100;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("expectedConsolidated.operatingResultMinor")));
});

test("rechaza costos compartidos asignados por encima del pool", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.businessUnitProfitability.businessUnits[0].sharedCostAllocationMinor += 1;
  fixture.scenarios.businessUnitProfitability.businessUnits[0].expectedOperatingResultMinor -= 1;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("shared allocation reconciliation")));
});


test("valida consumo interno entre áreas sin crear una venta externa", () => {
  const result = validateFixture(readFixture());
  assert.equal(result.valid, true, result.errors.join("\\n"));
  const fixture = readFixture();
  const scenario = fixture.scenarios.internalBusinessUnitTransfer;
  assert.equal(scenario.physicalInventoryMovementCount, 1);
  assert.equal(scenario.expectedConsolidatedExternalRevenueImpactMinor, 0);
});

test("rechaza doble movimiento físico en una transferencia interna", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.internalBusinessUnitTransfer.physicalInventoryMovementCount = 2;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("physicalInventoryMovementCount")));
});

test("rechaza una transferencia interna convertida en factura externa ficticia", () => {
  const fixture = structuredClone(readFixture());
  fixture.scenarios.internalBusinessUnitTransfer.createsFiscalInvoice = true;
  const result = validateFixture(fixture);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(message => message.includes("createsFiscalInvoice")));
});
