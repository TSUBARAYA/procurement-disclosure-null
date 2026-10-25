# 一键复现 Docker 镜像
# 构建: docker build -t procurement-disclosure-null .
# 运行: docker run --rm procurement-disclosure-null                     # 跑完整流水线
#       docker run --rm -v ${PWD}/paper:/app/paper procurement-disclosure-null make paper
# 注意: 容器内默认不下载 1.1GB 的 TED 原始数据。完整流水线（make all）需要
#       data/external/ted/ 下的 can_*.zip 与 cn_*.zip；缺失时 make data 会联网下载，
#       或按 README「第六轮/第八轮」说明预先放置。
FROM python:3.11-slim

WORKDIR /app

# 先装依赖（利用层缓存：依赖不变则不重装）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 项目文件。.dockerignore 排除 397MB 的 CN 匹配缓存与 34MB 阈值缓存，
# 两者由流水线自行生成（需要 TED 原始数据在位）。
COPY . .

# 容器内字体：matplotlib 的 serif/Times 回退到 DejaVu Serif，无需额外字体
ENV MPLBACKEND=Agg

# 默认执行完整流水线：结果 → 图 → 论文 docx → 466 项数字校验
CMD ["make", "all"]
