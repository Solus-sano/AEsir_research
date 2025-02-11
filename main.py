import os
import asyncio
from Agent.config import set_config, GLOBAL_CONFIG
import argparse

args = argparse.ArgumentParser()
args.add_argument("--research_query", type=str, default="调研一下目前图像生成领域的最新进展")
args.add_argument("--report_storage_path", type=str, default="report.md")
args.add_argument("--llm_module", type=str, default="gpt-4o-mini")
args.add_argument("--llm_base_url", type=str, default="https://api.gptsapi.net/v1")
args.add_argument("--llm_api_key", type=str, default="")
args.add_argument("--firecrawl_base_url", type=str, default="https://firecrawl.dev")
args.add_argument("--firecrawl_api_key", type=str, default="")
args.add_argument("--max_breadth", type=int, default=4)
args.add_argument("--max_depth", type=int, default=2)
args = args.parse_args()

set_config(args)

from Agent import dfs_research
import Agent.app_utils.llm_app as LLM_APP
from Agent.utils.log import log



logger = log.get_logger(__name__)


async def main(research_query, report_storage_path):
    logger.info(f"研究主题: {research_query}")
    logger.info(f"研究报告存储路径: {report_storage_path}")
    logger.info("开始研究...")
    res = await dfs_research.deep_research(
        research_query,
        breadth=GLOBAL_CONFIG.MAX_BREADTH,
        depth=GLOBAL_CONFIG.MAX_DEPTH
    )
    
    logger.info("研究完成，开始生成报告...")
    
    report_content = await LLM_APP.write_final_report(
        query=research_query,
        learnings=res['learnings'],
        visited_urls=res['visited_urls']
    )
    
    logger.info("报告生成完成")
    
    with open(report_storage_path, "w") as f:
        f.write(report_content)
    logger.info(f"报告已保存至: {report_storage_path}")
        
if __name__ == "__main__":
    
    
    asyncio.run(main(args.research_query, args.report_storage_path))