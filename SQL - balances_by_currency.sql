-- create or replace view balances_by_currency as
select * from (
	select
	    currency.name as currency
	    -- ,sum(combined.amount) as balance_small
		,sum(combined.amount)/power(10,currency.digits_after_decimal) as balance_large
		,ROUND((sum(combined.amount)/power(10,currency.digits_after_decimal))*currency.usd_per_large,0) AS value_usd
	from (
		select from_wallet_id as wallet_id, from_amount as amount
			from trans
			where from_amount is not null
		union all
		select to_wallet_id as wallet_id, to_amount as amount
			from trans
			where to_amount is not null
		union all
		select fee_wallet_id as wallet_id, fee_amount as amount
			from trans
			where fee_amount is not null
	) as combined
	left join wallet on combined.wallet_id = wallet.id
	left join currency on wallet.currency_id = currency.id
	group by currency.id
) as a
where balance_large != 0
order by value_usd desc;
