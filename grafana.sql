

select 
UNIX_TIMESTAMP(DATE_FORMAT(uptime,'%Y-%m-%d')) as time_sec, 
count(*) as value , 
'darknet' as metric 
from darknet_datasale 

GROUP BY  DATE_FORMAT(uptime,'%Y-%m-%d') 
ORDER BY metric desc




SELECT
  UNIX_TIMESTAMP(uptime) as time_sec,
  count(*) as value,
  (case
  when CONVERT(Time_format(uptime,'%H'),SIGNED) <= 6 THEN "0点-6点"
  when CONVERT(Time_format(uptime,'%H'),SIGNED) > 6 and CONVERT(Time_format(uptime,'%H'),SIGNED) <= 12 THEN "6点-12点"
  when CONVERT(Time_format(uptime,'%H'),SIGNED) > 12 and CONVERT(Time_format(uptime,'%H'),SIGNED) <= 18  THEN "12点-18点"
  when CONVERT(Time_format(uptime,'%H'),SIGNED) > 18 Then "18点-24点"
  end) as metric
FROM darknet_datasale
WHERE $__timeFilter(uptime)
group by (case
      when CONVERT(Time_format(uptime,'%H'),SIGNED) <= 6 THEN "0点-6点"
  when CONVERT(Time_format(uptime,'%H'),SIGNED) > 6 and CONVERT(Time_format(uptime,'%H'),SIGNED) <= 12 THEN "6点-12点"
  when CONVERT(Time_format(uptime,'%H'),SIGNED) > 12 and CONVERT(Time_format(uptime,'%H'),SIGNED) <= 18  THEN "12点-18点"
  when CONVERT(Time_format(uptime,'%H'),SIGNED) > 18 Then "18点-24点"
  end)
ORDER BY value desc


SELECT
  UNIX_TIMESTAMP(uptime) as time_sec,
  count(*) as value,
  (case
  when priceUSDT <= 1 THEN "$1以下"
  when priceUSDT > 1 and priceUSDT <= 20 THEN "$1-$20"
  when priceUSDT > 20 and priceUSDT <=100 THEN "$20-$100"
  when priceUSDT > 100 Then "大于$100"
  end) as metric
FROM darknet_datasale
WHERE $__timeFilter(uptime)
group by (case
  when priceUSDT <= 1 THEN "$1以下"
  when priceUSDT > 1 and priceUSDT <= 20 THEN "$1-$20"
  when priceUSDT > 20 and priceUSDT <=100 THEN "$20-$100"
  when priceUSDT > 100 Then "大于$100"
  end)
ORDER BY uptime ASC


select uptime,hot,title,sold,priceUSDT from darknet_datasale order by uptime desc ;
