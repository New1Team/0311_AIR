-- 항공사별_월별_지연분석
SELECT
    a.년도,
    a.월,
    a.항공사코드,
    u.설명 AS 항공사명,

    COUNT(*) AS 전체비행수,

    SUM(CASE WHEN a.출발지연시간 > 0 THEN 1 ELSE 0 END) AS 지연횟수,

    ROUND(
        SUM(CASE WHEN a.출발지연시간 > 0 THEN 1 ELSE 0 END)
        / COUNT(*) * 100
    ,2) AS 지연비율,

    AVG(CASE WHEN a.출발지연시간 > 0 THEN a.출발지연시간 END) AS 평균지연시간,

    MAX(a.출발지연시간) AS 최대지연시간

FROM db_to_air.항공지연분석 a
JOIN db_to_air.운반대 u
    ON a.항공사코드 = u.코드

GROUP BY
    a.년도,
    a.월,
    a.항공사코드,
    u.설명

ORDER BY
    a.년도,
    a.월,
    지연비율 DESC;

-- 항공사별_연도별_지연 출발공항/도시

SELECT
    a.년도,
    a.항공사코드,
    u.설명 AS 항공사명,
    a.출발공항코드,
    COUNT(*) AS 지연횟수,
    AVG(a.출발지연시간) AS 평균지연시간
FROM db_to_air.항공지연분석 a
JOIN db_to_air.운반대 u
    ON a.항공사코드 = u.코드
WHERE a.출발지연시간 > 0
GROUP BY
    a.년도,
    a.항공사코드,
    u.설명,
    a.출발공항코드
ORDER BY
    a.년도,
    항공사명,
    지연횟수 DESC;

-- 항공사별_월별_지연리스크3단계

SELECT
    a.년도,
    a.월,
    a.항공사코드,
    u.설명 AS 항공사명,

    COUNT(*) AS 전체비행수,

    SUM(CASE
            WHEN a.출발지연시간 > 0
             AND a.출발지연시간 <= 30
            THEN 1
            ELSE 0
        END) AS risk1_경미,

    SUM(CASE
            WHEN a.출발지연시간 > 30
             AND a.출발지연시간 < 180
            THEN 1
            ELSE 0
        END) AS risk2_보통,

    SUM(CASE
            WHEN a.출발지연시간 >= 180
            THEN 1
            ELSE 0
        END) AS risk3_위험

FROM db_to_air.항공지연분석 a
JOIN db_to_air.운반대 u
    ON a.항공사코드 = u.코드

GROUP BY
    a.년도,
    a.월,
    a.항공사코드,
    u.설명

ORDER BY
    a.년도,
    a.월,
    a.항공사코드;

-- 항공사별 공항 위치 분포

SELECT DISTINCT *
FROM 공항2
ORDER BY 1, 2;

-- 연도별 항공사 지연 리스크

SELECT *
FROM risk_level

-- 우회 데이터

 select 
        d.`년도`, 
        d.`월`, 
        d.`일`, 
        d.`요일`, 
        d.`항공사코드`,
        d.`항공편번호`,
        d.`출발공항코드`,
        d.`도착지공항코드`,
        d.`비행거리`
        FROM `항공우회분석` AS d
        
        ORDER BY d.`년도`,d.`월`

-- 취소율 데이터

 SELECT `년도`, `월`, `일`, `요일`, `항공사코드`, `항공편번호`, `출발공항코드` 
        FROM `항공취소분석` 
        WHERE `년도` = {year} 
        AND `항공사코드` = '{airline}'