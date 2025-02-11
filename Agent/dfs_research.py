import sys
sys.path.append(".")

import asyncio
from typing import List, Dict, Any, Optional
from collections.abc import Iterable
from Agent.app_utils.firecrawl_app import Crawl_app
import Agent.app_utils.llm_app as LLM_APP
from Agent.utils.log import log
from Agent.config import GLOBAL_CONFIG

logger = log.get_logger(__name__)

def compact(input_list: List[Optional[Any]]) -> List[Any]:
    return [item for item in input_list if item]

ResearchResult = Dict[str, List[str]]


async def deep_research(
    query: str,
    breadth: int, 
    depth: int, 
    learnings: Optional[List[str]] = None, 
    visited_urls: Optional[List[str]] = None
    ) -> ResearchResult:

    if learnings is None:
        learnings = []
    if visited_urls is None:
        visited_urls = []

    serp_queries = await LLM_APP.get_serp_queries(
        query=query,
        learnings=learnings,
        num_queries=breadth
    )
    logger.info(f"生成的 SERP 查询: {serp_queries}")
    
    limit_sem = asyncio.Semaphore(GLOBAL_CONFIG.ConcurrencyLimit) # 创建信号量来限制并发

    async def process_query(serp_query: Dict[str, str]) -> ResearchResult:
        async with limit_sem: # 使用信号量限制并发
            try:
                result = Crawl_app.search(serp_query['query'], {
                    'timeout': 15000,
                    'limit': 5,
                    'scrapeOptions': {'formats': ['markdown']}
                })

                # 从本次搜索中收集 URLs
                new_urls_optional = [item.get('url') for item in result['data']]
                new_urls = compact(new_urls_optional) # 移除 None 值等
                new_breadth = max(1, breadth // 2) # 确保 new_breadth 至少为 1
                new_depth = depth - 1

                new_learnings_result = await LLM_APP.process_serp_result(
                    query=serp_query['query'],
                    result=result,
                    num_follow_up_questions=new_breadth
                )
                all_learnings = learnings + new_learnings_result['learnings']
                all_urls = visited_urls + new_urls
                
                # logger.info(f"目前所有learning: {all_learnings}")

                if new_depth > 0:
                    print(f"深入研究，广度: {new_breadth}, 深度: {new_depth}")
                    next_query = f"""
                    之前的研究目标: {serp_query['researchGoal']}
                    后续研究方向: {''.join([f'\n{q}' for q in new_learnings_result['followUpQuestions']])}
                    """.strip()

                    return await deep_research(
                        query=next_query,
                        breadth=new_breadth,
                        depth=new_depth,
                        learnings=all_learnings,
                        visited_urls=all_urls
                    )
                else:
                    return {
                        'learnings': all_learnings,
                        'visited_urls': all_urls
                    }

            except Exception as e:
                error_message = str(e)
                if 'Timeout' in error_message:
                    logger.info(f"查询超时错误: {serp_query['query']}: {e}")
                else:
                    logger.info(f"查询错误: {serp_query['query']}: {e}")
                return {
                    'learnings': [],
                    'visited_urls': []
                }

    results = await asyncio.gather(*[process_query(serp_query) for serp_query in serp_queries])

    # 汇总所有结果并去重
    all_learnings_final = list(set(sum([r['learnings'] for r in results], []))) # 使用 sum(..., []) 展平列表
    all_visited_urls_final = list(set(sum([r['visited_urls'] for r in results], [])))

    return {
        'learnings': all_learnings_final,
        'visited_urls': all_visited_urls_final
    }

async def main():
    initial_query = "流萤角色分析"
    logger.info(f"初始查询: {initial_query}")
    research_result = await deep_research(query=initial_query, breadth=4, depth=2)
    print("\n最终研究结果:")
    print("学到的知识:", research_result['learnings'])
    print("访问过的 URLs:", research_result['visited_urls'])

if __name__ == "__main__":
    asyncio.run(main())