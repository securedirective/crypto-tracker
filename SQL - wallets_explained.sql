-- create or replace view wallets_explained as
SELECT
	wallet.id AS wallet_id
	,ident.name AS ident_name
	,seed.name AS seed_name
	,CONCAT(currency.unit_large, " (", currency.name, ")", IFNULL(CONCAT(" - ", wallet.passphrase),"")) AS currency_description
	-- ,CONCAT(seed.name, " > ", currency.unit_large, " (", currency.name, ")") AS wallet_description
	-- ,wallet.old_name AS wallet_name
	,seed.level_of_trust AS seed_level_of_trust
FROM wallet
LEFT JOIN currency ON wallet.currency_id=currency.id
LEFT JOIN seed ON wallet.seed_id=seed.id
LEFT JOIN ident ON seed.identity_id=ident.id
ORDER BY ident_name, seed_name, currency_description
-- ORDER BY wallet_description
