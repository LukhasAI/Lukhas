# products/MANIFEST.md

This manifest maps consolidated `products/` structure to current scattered locations.

Consolidation eliminates redundant lambda_core/ and lambda_products/ layers.

Format: products/new/path -> current/source/path

## Intelligence Products (Analytics & Monitoring)
- intelligence/argus -> products/lambda_products/lambda_products_pack/lambda_core/ARGUS
- intelligence/dast -> products/lambda_products/lambda_products_pack/lambda_core/DAST
- intelligence/dast_enhanced -> products/lambda_products/lambda_products_pack/lambda_core/DAST_ENHANCED

## Communication Products (Messaging & Social)
- communication/nias -> products/lambda_products/lambda_products_pack/lambda_core/NIAS
- communication/abas -> products/lambda_products/lambda_products_pack/lambda_core/ABAS

## Content Products (Generation & Creativity)
- content/auctor -> products/lambda_pack/auctor
- content/poetica -> products/lambda_products/lambda_products_pack/lambda_core/POETICA

## Infrastructure Products (Systems & Operations)
- infrastructure/trace -> products/lambda_products/lambda_products_pack/lambda_core/TRACE
- infrastructure/legado -> products/lambda_products/lambda_products_pack/lambda_core/LEGADO
- infrastructure/nimbus -> products/lambda_products/lambda_products_pack/lambda_core/NIMBUS

## Security Products (Protection & Finance)
- security/guardian -> products/lambda_products/lambda_products_pack/lambda_core/Guardian
- security/wallet -> products/lambda_products/lambda_products_pack/lambda_core/WALLET

## Development Lane Implementations (candidate/)
- candidate/intelligence/argus -> candidate/core/architectures/argus (if exists)
- candidate/intelligence/dast -> candidate/core/architectures/dast
- candidate/communication/nias -> candidate/core/architectures/nias
- candidate/communication/abas -> candidate/core/architectures/abas

Additional scattered implementations will be consolidated into the above structure.
