# db_to_air 테이블생성
USE db_to_air;

CREATE TABLE 공항 (
항공사코드 VARCHAR(50),
공항코드 VARCHAR(100),
위도 INT,
경도 INT
);

CREATE TABLE 항공우회분석 (
id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
년도 INT,
월 INT,
일 INT,
요일 INT,
항공사코드 VARCHAR(10),
항공편번호 INT,
출발공항코드 VARCHAR(10),
도착지공항코드 VARCHAR(10)
);

CREATE TABLE 항공취소분석 (
id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
년도 INT,
월 INT,
일 INT,
요일 INT,
항공사코드 VARCHAR(10),
항공편번호 INT,
출발공항코드 VARCHAR(10)
);


CREATE TABLE 항공지연분석 (
id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
년도 VARCHAR(100),
월 INT,
일 INT,
요일 INT,
항공사코드 VARCHAR(10),
항공편번호 INT,
출발공항코드 VARCHAR(10),
도착지공항코드 VARCHAR(10),
예정db_to_air출발시간 INT,
실제출발시간 INT,
출발지연시간 INT,
도착지연시간 INT,
비행거리 INT
);

CREATE TABLE 운반대(
코드 VARCHAR(10),
설명 VARCHAR(50)
);

# db_air2 to db_to_air 적재

INSERT INTO db_to_air.`공항`
SELECT * FROM db_air2.`공항`;

INSERT INTO db_to_air.운반대
SELECT * FROM db_air2.운반대;

INSERT INTO db_to_air.`항공취소분석`
SELECT * FROM db_air2.`항공취소db_to_air`항공지연분석`분석`;

INSERT INTO db_to_air.`항공우회분석`
SELECT * FROM db_air2.`항공우회분석2`;

INSERT INTO db_to_air.`항공지연분석`
(
id,
년도,
월,
일,
요일,
항공사코드,
항공편번호,
출발공항코드,
도착지공항코드,
예정출발시간,
실제출발시간,
출발지연시간,
도착지연시간,
비행거리
)
SELECT id,
년도,
월,
일,
요일,
항공사코드,
항공편번호,
출발공항코드,
도착지공항코드,
예정출발시간,
실제출발시간,
출발지연시간,
도착지연시간,
비행거리 FROM db_air2.`항공지연분석`;

# 뷰 이동
CREATE VIEW db_to_air.view_항공사별_지연_risk_단계분석 AS
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