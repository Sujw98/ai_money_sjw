create database if not exists `xiaohongshu_caijing`;

CREATE TABLE outlines (
        id INTEGER NOT NULL AUTO_INCREMENT,
        resource_name VARCHAR(255) NOT NULL COMMENT '资源名称（书籍/课程名）',
        resource_type VARCHAR(50) COMMENT '资源类型',
        total_topics INTEGER COMMENT '总主题数量',
        completed_topics INTEGER COMMENT '已完成主题数',
        description TEXT COMMENT '大纲描述',
        created_at DATETIME COMMENT '创建时间',
        updated_at DATETIME COMMENT '更新时间',
        PRIMARY KEY (id)
)


CREATE TABLE topics (
        id INTEGER NOT NULL AUTO_INCREMENT,
        outline_id INTEGER NOT NULL COMMENT '所属大纲ID',
        topic_title VARCHAR(255) NOT NULL COMMENT '主题标题',
        topic_content TEXT COMMENT '主题详细内容/要点',
        order_index INTEGER NOT NULL COMMENT '顺序索引',
        status ENUM('PENDING','PROCESSING','COMPLETED','FAILED') COMMENT '处理状态',
        keywords VARCHAR(500) COMMENT '关键词（用于搜索）',
        created_at DATETIME COMMENT '创建时间',
        updated_at DATETIME COMMENT '更新时间',
        PRIMARY KEY (id),
        FOREIGN KEY(outline_id) REFERENCES outlines (id)
)


CREATE TABLE inspirations (
        id INTEGER NOT NULL AUTO_INCREMENT,
        topic_id INTEGER NOT NULL COMMENT '所属主题ID',
        xhs_note_id VARCHAR(100) COMMENT '小红书笔记ID',
        title VARCHAR(500) COMMENT '笔记标题',
        content TEXT COMMENT '笔记内容摘要',
        author VARCHAR(100) COMMENT '作者昵称',
        likes INTEGER COMMENT '点赞数',
        collects INTEGER COMMENT '收藏数',
        comments INTEGER COMMENT '评论数',
        url VARCHAR(500) COMMENT '笔记链接',
        created_at DATETIME COMMENT '创建时间',
        PRIMARY KEY (id),
        FOREIGN KEY(topic_id) REFERENCES topics (id)
)


CREATE TABLE contents (
        id INTEGER NOT NULL AUTO_INCREMENT,
        topic_id INTEGER NOT NULL COMMENT '所属主题ID',
        raw_title VARCHAR(500) COMMENT '原始标题',
        raw_content TEXT COMMENT '原始内容',
        optimized_title VARCHAR(500) COMMENT '优化后标题',
        optimized_content TEXT COMMENT '优化后内容',
        tags VARCHAR(500) COMMENT '标签（逗号分隔）',
        created_at DATETIME COMMENT '创建时间',
        updated_at DATETIME COMMENT '更新时间',
        PRIMARY KEY (id),
        FOREIGN KEY(topic_id) REFERENCES topics (id)
)

CREATE TABLE publish_records (
        id INTEGER NOT NULL AUTO_INCREMENT,
        content_id INTEGER NOT NULL COMMENT '内容ID',
        xhs_note_id VARCHAR(100) COMMENT '小红书笔记ID',
        publish_time DATETIME COMMENT '发布时间',
        status ENUM('SUCCESS','FAILED','PENDING') COMMENT '发布状态',
        error_message TEXT COMMENT '错误信息',
        retry_count INTEGER COMMENT '重试次数',
        created_at DATETIME COMMENT '创建时间',
        PRIMARY KEY (id),
        FOREIGN KEY(content_id) REFERENCES contents (id)
)
