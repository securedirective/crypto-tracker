select * from (
	select
	    currency.name as currency
	    ,wallet.id as id
	    ,wallet.name as wallet
	    ,sum(combined.amount) as balance_small
		,sum(combined.amount)/power(10,currency.digits_after_decimal) as balance_large
		,ROUND((sum(combined.amount)/power(10,currency.digits_after_decimal))*currency.usd_per_large,2) AS value_usd
		,wallet.level_of_trust
	from (
		select from_wallet_id as wallet_id, from_amount as amount
			from trans
			where from_amount is not null and date_utc < '2017-10-24 00:00:00'
		union all
		select to_wallet_id as wallet_id, to_amount as amount
			from trans
			where to_amount is not null and date_utc < '2017-10-24 00:00:00'
		union all
		select fee_wallet_id as wallet_id, fee_amount as amount
			from trans
			where fee_amount is not null and date_utc < '2017-10-24 00:00:00'
	) as combined
	left join wallet on combined.wallet_id = wallet.id
	left join currency on wallet.currency_id = currency.id
	group by wallet.id
	order by currency, wallet
) as a
where balance_small != 0
order by value_usd desc;
