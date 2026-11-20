import { resolve } from "node:path";
import { defaultFixturePath, readFixture, validateFixture } from "./fixture-validator.mjs";

const fixturePath = process.argv[2] ? resolve(process.argv[2]) : defaultFixturePath;

let fixture;
try {
  fixture = readFixture(fixturePath);
} catch (error) {
  console.error("No se pudo leer el dataset: " + error.message);
  process.exitCode = 1;
}

if (fixture !== undefined) {
  const result = validateFixture(fixture);
  if (!result.valid) {
    console.error("Dataset de evaluación inválido:");
    for (const message of result.errors) console.error(" - " + message);
    process.exitCode = 1;
  } else {
    console.log("Dataset de evaluación válido.");
    console.log(
      result.summary.articleCount + " artículos; " +
      result.summary.mixedPaymentLines + " líneas; " +
      result.summary.scenarioCount + " escenarios; " +
      result.summary.paymentTransactionCount + " intentos de pago sintéticos; " +
      result.summary.currency + "; " + result.summary.locale + "."
    );
  }
}
