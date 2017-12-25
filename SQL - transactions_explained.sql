-- create or replace view transactions_explained as
select
	trans.id,
	date_utc,
	trans_type,
	from_wallet.name as from_wallet,
	to_wallet.name as to_wallet,
	from_amount / power(10, from_currency.digits_after_decimal) as from_amount,
	to_amount / power(10, to_currency.digits_after_decimal) as to_amount,
	fee_amount / power(10, fee_currency.digits_after_decimal) as fee_amount,
	-- if(fee_wallet.name != from_wallet.name, concat("fee paid from ", fee_wallet.name), null) as fee_paid_from,
	trans.notes,
	replace(from_currency.info_tx, '%s', trans.from_txid) as from_tx,
	replace(to_currency.info_tx, '%s', trans.to_txid) as to_tx
from trans
left join wallet from_wallet on from_wallet_id = from_wallet.id
left join currency from_currency on from_wallet.currency_id = from_currency.id
left join wallet to_wallet on to_wallet_id = to_wallet.id
left join currency to_currency on to_wallet.currency_id = to_currency.id
left join wallet fee_wallet on fee_wallet_id = fee_wallet.id
left join currency fee_currency on fee_wallet.currency_id = fee_currency.id
order by date_utc
