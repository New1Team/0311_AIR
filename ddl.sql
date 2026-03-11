# 공항 MAP 제작 위한 쿼리
SELECT distinct a.항공사코드, a.출발공항코드 AS 공항, air.위도, air.경도
from db_air2.`비행` as a
join db_air2.`항공사` as air
ON (a.`출발공항코드` = air.항공사코드)
ORDER BY a.항공사코드, a.`출발공항코드`
;