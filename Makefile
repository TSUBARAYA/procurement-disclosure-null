# 一键复现：论文全部数值结果、图与 Word 文档
#
#   make all        完整流水线（数据 → 结果 → 图 → 论文 → 校验）
#   make data       下载 11 年 TED CAN + CN 原始数据（约 1.1GB，需网络）
#   make results    全部数值结果（v3/v4 转化设计、v6.0 归档复现、v7.0 主设计、诊断）
#   make figures    重绘 5 张学术图（matplotlib，冷色调，300dpi）
#   make paper      由 Markdown 生成 docx（TNR、两端对齐、表格、图片）
#   make verify     537 项数字对回归档 JSON 校验
#   make clean      删除生成物
#
# 依赖: python3 + numpy/pandas/scipy/matplotlib/python-docx（见 requirements.txt）
# Docker: docker build -t procurement-disclosure-null . && docker run --rm procurement-disclosure-null

PY := python3
FIG := figures
PAPER := paper
AN := analysis
TED := data/external/ted
CACHE_CAN := analysis/rd_sample_cache.csv
CACHE_CN := analysis/cn_matched_clean.csv
YEARS := 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023

.PHONY: all data results figures paper verify clean

all: data results figures paper verify

# ---------------------------------------------------------------- 原始数据
# EU Open Data Portal 的 TED 年度 extract。CAN = 合同授标公告（75 列），
# CN = 合同招标公告（64 列，含开标前法定估计价值 VALUE_EURO，v7.0 主设计的
# running variable 来源）。两者都要下载。
data: $(TED)/can_2013.zip $(TED)/cn_2013.zip
	@echo "TED 原始数据就绪（$(words $(YEARS)) 年 × CAN+CN）"

$(TED)/can_%.zip:
	@mkdir -p $(TED)
	curl -sSL -o $@ "https://data.europa.eu/api/hub/store/data/ted-contract-award-notices-$*.zip"

$(TED)/cn_%.zip:
	@mkdir -p $(TED)
	curl -sSL -o $@ "https://data.europa.eu/api/hub/store/data/ted-contract-notices-$*.zip"

# ---------------------------------------------------------------- 数值结果
# 每个脚本都可独立重跑；输出全部落 materials/results/*.json
results: $(CACHE_CN) $(CACHE_CAN)
	$(PY) identification/run_v3.py            # v3.0 国家年面板 ATT（252 箱）
	$(PY) identification/run_v4.py            # v4.0 合同级 TWFE + 剂量反应
	$(PY) $(AN)/run_v6_full_rerun.py          # v6.0 归档复现 + 法定阈值重跑
	$(PY) $(AN)/run_v6_rerun_final.py         # v6.0 全套诊断
	$(PY) $(AN)/run_v7_estimate_rd.py         # v7.0 主设计：法定估计价值 RD
	$(PY) $(AN)/run_v7_clean_subsamples.py    # 清洗 + 覆盖率 + 子样本分解
	$(PY) $(AN)/run_v7_scale_placebo.py       # 规模效应 + 安慰剂复核
	$(PY) $(AN)/run_v7_placebo_bunching.py    # placebo battery + bunching 重建
	$(PY) $(AN)/run_v3_inference_and_audit.py # v3.0 原生推断 + 可复现性审计
	$(PY) $(AN)/run_transposition_redesign.py # 转化设计：国家年面板 + 事件研究
	$(PY) $(AN)/run_transposition_contract.py # 转化设计：合同级事件研究
	$(PY) $(AN)/run_transposition_never.py    # 转化设计：never-treated 对照
	$(PY) $(AN)/run_v7_first_stage.py         # 第一阶段：程序结构 15 候选 + Holm
	$(PY) $(AN)/run_v7_density_robust.py      # McCrary 密度 + binscatter + 高发布子样本
	$(PY) $(AN)/run_v7_density_test.py        # 局部密度检验（1/2 箱 + 聚类 bootstrap）
	$(PY) $(AN)/run_review9_coverage.py       # CN 估值覆盖率分母（原始 zip 单遍）
	$(PY) $(AN)/run_review9_paper_numbers.py  # 论文定稿补算（平衡/堆点/MDE/清洗分解）
	$(PY) $(AN)/run_review9_loo.py            # v7.0 留一国法（28 国逐个剔除）
	$(PY) $(AN)/run_review9_offer_robust.py   # n_offers 稳健性诊断（winsorize/log/带宽）
	$(PY) $(AN)/run_review9_density_slope.py  # 密度斜率诊断（continuity 威胁评估）
	$(PY) $(AN)/run_review9_figures_v7.py     # v7.0 图数据重建（28 国缓存）
	$(PY) identification/run_v6.py            # v6.0 归档口径端到端复现（写 report/）
	@echo "全部结果已写入 materials/results/（run_v3/v4/v6 的复现校验写 report/）"

# 中间缓存：CN-CAN 匹配样本（4.69M 行，28 国含希腊）。由 run_v7_estimate_rd.py 生成，
# 单独列为目标以便 results 依赖它。
$(CACHE_CN): $(TED)/can_2013.zip $(TED)/cn_2013.zip
	$(PY) $(AN)/run_v7_estimate_rd.py

# v6.0 归档口径的 ±20% 带缓存（34MB）。缺失时相关脚本会自行从 TED 重建。
$(CACHE_CAN): $(TED)/can_2013.zip
	@if [ ! -f $@ ]; then echo "未找到 $@，相关脚本将从原始 TED 重建"; fi

# ---------------------------------------------------------------- 图与论文
figures:
	$(PY) $(FIG)/redraw_figures.py

paper: figures
	$(PY) $(PAPER)/md2docx.py

verify: paper
	$(PY) $(PAPER)/verify_round4.py

clean:
	rm -f $(FIG)/fig*.png $(PAPER)/*.docx
	rm -f $(CACHE_CN) $(AN)/cn_matched.csv $(AN)/micro_exact.csv
	rm -f $(AN)/cy_panel_exact.csv $(AN)/ted_wide_final.csv
