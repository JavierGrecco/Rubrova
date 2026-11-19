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
