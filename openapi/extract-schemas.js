#!/usr/bin/env node

import { readFileSync, writeFileSync } from "fs";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
// Now explicitly require from the CWD's node_modules:
const yaml = require(process.cwd() + "/node_modules/js-yaml");

// Read and parse OpenAPI spec
const __dirname = dirname(fileURLToPath(import.meta.url));
const openapiPath = resolve(__dirname, "../openapi/components.yaml");
const openapiContent = readFileSync(openapiPath, "utf8");
const openapiSpec = yaml.load(openapiContent);

// Extract schemas
const schemas = openapiSpec.components?.schemas || {};

// Generate TypeScript module content
let tsContent = `/**
 * This file was auto-generated from components.yaml
 * Do not make direct changes to the file.
 */

`;

// Export each schema as a const for tree-shaking
for (const [schemaName, schemaDefinition] of Object.entries(schemas)) {
  tsContent += `export const ${schemaName}Schema = ${JSON.stringify(schemaDefinition, null, 2)} as const;\n\n`;
}

// Also export all schemas as a single object for convenience
tsContent += `export const schemas = {\n`;
for (const schemaName of Object.keys(schemas)) {
  tsContent += `  ${schemaName}: ${schemaName}Schema,\n`;
}
tsContent += `} as const;\n`;

// Write TypeScript file
const outputPath = resolve(process.cwd(), "src/schemas.ts");
writeFileSync(outputPath, tsContent, "utf8");
console.log(`✓ Generated ${outputPath}`);
