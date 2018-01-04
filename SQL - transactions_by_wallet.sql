SELECT
	combined.date
    ,wallet.name AS wallet
    ,combined.amount AS amount_small
	,combined.amount/POWER(10,currency.digits_after_decimal) AS amount_large
	-- ,combined.from_txid
	-- ,combined.to_txid
	,combined.dir
	,combined.notes
FROM (
	SELECT date, 'from' AS t, from_wallet_id AS wallet_id, from_amount AS amount, from_txid, '' AS to_txid, 'a-decrease' AS dir, notes
		FROM `trans`
		WHERE from_amount IS NOT NULL
	UNION ALL
	SELECT date, 'to' AS t, to_wallet_id AS wallet_id, to_amount AS amount, '' AS from_txid, to_txid, 'b-increase' AS dir, notes
		FROM `trans`
		WHERE to_amount IS NOT NULL
	UNION ALL
	SELECT date, 'fee' AS t, fee_wallet_id AS wallet_id, fee_amount AS amount, '', '', 'c-FEE' AS dir, notes
		FROM trans
		WHERE fee_amount IS NOT NULL
) AS combined
LEFT JOIN wallet ON combined.wallet_id = wallet.id
LEFT JOIN currency ON wallet.currency_id = currency.id
-- WHERE wallet.name = 'BTC_NanoS1'
WHERE currency.unit_large = 'BTC'
ORDER BY combined.date, combined.dir;
