# redis_cache
基于python+mysql+redis缓存设计
测试环境
redis-5.0.5
macos
python 3.7
mysql 5.7

基于Python操作Redis
1、 创建示例数据库表
CREATE TABLE tb_signin_rank(
id INT,
user_name VARCHAR(10) COMMENT '用户名',
signin_num INT COMMENT '签到次数',
signin_time DATETIME COMMENT '签到时间',
gold_coin INT COMMENT '金币'
);
 
初始化数据
INSERT INTO tb_signin_rank
VALUES(1, 'shouke', 0, NULL, 0),
(2, 'chuangke', 0, NULL, 0),
(3, 'ishouke', 0, NULL, 0),
(4, 'keshou', 0, NULL, 0),
(5, 'shouke', 0, NULL, 0);
2、 redis缓存键值设计
key               value
表名:主键值:列名   列值
 
或者如下，通过为不同列之间建立较为紧密的关联
key                        value
表名:主键值:列值1:列名2   列值2
  
示例：把id为1的人的签到次数(假设为5)存储到redis中则可如下操作：
set('tb_signin_rank:1:signin_num', 5)
 
这样做的好处是，类似数据库一样，通过主键便可获取其它值。
 
示例：把id和用户名关联
set('tb_signin_rank:shouke:id', 1)
 
这样，通过用户名就可以查询出关联的id了：uid = r.get("tb_signin_rank:%s:id" % username)
 
3、 redis关联数据库的数据处理
 
不要求强一致实时性的读请求，都由redis处理
要求强一致实时性的读请求，由数据库处理
通常包含以下两种处理模式：
模式1：先判断是否存在缓存(通常是根据key)，如果存在则从缓存读取，否则从数据库读取并更新缓存。
适用场景：对数据实时性要求不高，更新比较不频繁，比如签到排行榜
 
模式2：
先写入redis然后，利用守护进程等方式，定时写入到数据库

模式3：
先写入数据库，然后再更新到缓存
适用场景：数据量较大，更新较为频繁
 
说明：
模式2和模式3的区别在于，前者把redis当作数据库用，通过写入redis后马上返回程序，
然后定时把数据写入数据库，这也大大提高了访问速度。
这种方式不足的是，这种对redis的可靠性依赖性太强
