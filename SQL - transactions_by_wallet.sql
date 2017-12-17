select * from (
	select
		combined.date_utc
	    ,wallet.name as wallet
	    ,combined.amount as balance_small
		,combined.amount/power(10,currency.digits_after_decimal) as balance_large
		-- ,combined.from_txid
		-- ,combined.to_txid
		,combined.trans_type
		,combined.notes
	from (
		select date_utc, 'from' as t, from_wallet_id as wallet_id, from_amount as amount, from_txid, '' as to_txid, '1-SEND' as trans_type, notes
			from `trans`
			where from_amount is not null
		union all
		select date_utc, 'to' as t, to_wallet_id as wallet_id, to_amount as amount, '' as from_txid, to_txid, '2-RECV' as trans_type, notes
			from `trans`
			where to_amount is not null
		union all
		select date_utc, 'fee' as t, fee_wallet_id as wallet_id, fee_amount as amount, '', '', '3-FEE' as trans_type, notes
			from trans
			where fee_amount is not null
	) as combined
	left join wallet on combined.wallet_id = wallet.id
	left join currency on wallet.currency_id = currency.id
	where wallet.name like 'WalletNameHere'
) as a
order by date_utc, trans_type;
