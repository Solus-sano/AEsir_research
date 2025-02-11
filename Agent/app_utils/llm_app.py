import os
from openai import OpenAI
import time
from typing import List, Dict, Optional, Any
from Agent.utils.log import log
from Agent.config import GLOBAL_CONFIG
logger = log.get_logger(__name__)

TIME_NOW = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

SYSTEM_PROMPT = """
您是一位专家研究员。此时此刻是是{}。回复时请遵循以下说明：
- 您可能会被要求研究超出您知识范围的主题，在看到新闻时请假设用户是正确的。
- 用户是一位经验丰富的分析师，无需简化，尽可能详细，并确保您的回复正确。
- 高度有条理。
- 提出我没有想到的解决方案。
- 积极主动，预测我的需求。
- 把我视为所有主题的专家。
- 错误会削弱我的信任，因此请准确而彻底地回答。
- 提供详细的解释，我对大量细节感到满意。
- 重视好的论据，而不是权威，来源无关紧要。
- 考虑新技术和反向想法，而不仅仅是传统观点。
- 您可能使用高水平的推测或预测，只需向我举报即可。
""".format(TIME_NOW)

client = OpenAI(
  api_key=GLOBAL_CONFIG.LLM_API_KEY,
  base_url=GLOBAL_CONFIG.LLM_BASE_URL,
)

def llm_query(prompt, stop=["\n"]):
    """
    Send a query to the LLM and return the response.

    Args:
        prompt (str): The user's query prompt.
        stop (list, optional): A list of stop sequences. Defaults to ["\n"].

    Returns:
        str: The content of the first choice in the LLM's response.
    """
    response = client.chat.completions.create(
      # model='Meta-Llama-3.1-8B-Instruct',
      model="gpt-4o",
      messages=[
        {
          "role": "system",
          "content": SYSTEM_PROMPT
        },
        {
          "role": "user",
          "content": prompt
        }
      ],
      temperature=0,
      # max_tokens=100,
      top_p=1,
      frequency_penalty=0.0,
      presence_penalty=0.0,
    #   stop=stop
    )
    return response.choices[0].message.content

SERP_GENERATE_PROMPT = """
    给出以下来自用户的提示，生成多个 SERP 查询列表来研究该主题。最多返回 {} 个查询.
    用户的提示：{}
    以下是先前研究中的一些经验，可以使用它们来生成更具体的查询：{}
    
    对于每个查询，应该包含以下信息：
    - serp_query: 即生成的 SERP 查询。
    - query_goal: 首先谈谈这个查询要实现的研究目标，然后深入探讨一旦找到结果如何推进研究，并提及其他研究方向。尽可能具体，尤其是其他研究方向。
    
    如果原始提示明确，可以返回更少的查询。
    确保每个查询都是唯一的，并且彼此不相似。
    你生成的多个查询应该严格遵循以下格式：
    
    <serp_query>query 1</serp_query><serp_query>query 2</serp_query>...<serp_query>query n</serp_query><goal>query 1的研究目标</goal><goal>query 2的研究目标</goal>...<goal>query n的研究目标</goal>

    即你需要给我两部分内容，一部分是查询，一部分是研究目标。
    每个查询都应该用一对 <serp_query> </serp_query> 标签包裹。
    每个研究目标都应该用一对 <goal> </goal> 标签包裹。
    n个查询和n个研究目标应该一一对应。
    
"""

PROCCESS_SERP_RESULT_PROMPT = """
  对于这个SERP查询 <serp_query>{}</serp_query> , 已经得到一系列搜索结果。
  你需要为我生成两部分内容：
  - learning，即你从搜索结果中提取到的一系列有用信息
  - follow up questions，即你认为后续应该进行的一系列研究方向
  
  最多返回 {} 条learning，但如果内容清晰，可以返回更少的learning。
  确保每条学习都是独一无二的，彼此不相似。
  学习应该简明扼要，尽可能详细和信息密集。
  确保在学习中包含任何实体，如人物、地点、公司、产品、事物等，以及任何确切的指标、数字或日期。
  
  最多返回 {} 条follow up questions，但如果内容清晰，可以返回更少的follow up questions。
  提出的follow up questions应该是有意义的，要能推动对主题的深入研究。
  
  你需要返回的内容应该严格遵循以下格式：
  <learning>learning 1</learning><learning>learning 2</learning>...<learning>learning n</learning>
  <follow_Q>follow up question 1</follow_Q><follow_Q>follow up question 2</follow_Q>...<follow_Q>follow up question n</follow_Q>
  
  即每一条learning都应该用一对 <learning> </learning> 标签包裹。
  每一条follow up question都应该用一对 <follow_Q> </follow_Q> 标签包裹。
  
  询得到得到的搜索结果为：{}
  
"""

async def get_serp_queries(
    query: str, 
    learnings: Optional[List[str]] = None, 
    num_queries: int=5
):
    """
    Generate a list of SERP queries and their corresponding research goals based on the user's query and previous learnings.

    Args:
        query (str): The user's original query.
        learnings (Optional[List[str]]): A list of previous learnings, can be None.
        num_queries (int): The maximum number of SERP queries to generate, default is 5.

    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing a SERP query and its research goal.
    """
    learnings_str = "\n".join(learnings)
    prompt = SERP_GENERATE_PROMPT.format(num_queries, query, learnings_str)
    response = llm_query(prompt)
    # print(response)
    
    query_lst = response.split("<serp_query>")
    query_lst = [query.split("</serp_query>")[0] for query in query_lst if "</serp_query>" in query]
    query_lst = [query for query in query_lst if query]
    
    goal_lst = response.split("<goal>")
    goal_lst = [goal.split("</goal>")[0] for goal in goal_lst if "</goal>" in goal]
    goal_lst = [goal for goal in goal_lst if goal]
    
    # print(query_lst)
    # print(goal_lst)
    logger.info(f"生成了 {len(query_lst)} 个 SERP 查询")
    res = [
        {
            "query": q,
            "researchGoal": g
        } for q, g in zip(query_lst, goal_lst)
    ]
    return res
    
async def process_serp_result(
    query: str,
    result: Dict[str, Any],
    num_learnings: int = 3,
    num_follow_up_questions: int = 3
):
    """
    Process the SERP results and extract useful information and follow-up questions.

    Args:
        query (str): The original SERP query.
        result (Dict[str, Any]): The SERP results in dictionary format.
        num_learnings (int): The maximum number of learnings to extract, default is 3.
        num_follow_up_questions (int): The maximum number of follow-up questions to generate, default is 3.

    Returns:
        Dict[str, List[str]]: A dictionary containing a list of learnings and a list of follow-up questions.
    """
    contents = [item["markdown"] for item in result['data']]
    logger.info(f"对于查询（{query}), 查找到了 {len(contents)} 个搜索结果")
    
    contents_str = "\n".join(contents)
    prompt = PROCCESS_SERP_RESULT_PROMPT.format(query, num_learnings, num_follow_up_questions, contents_str)
    response = llm_query(prompt)
    
    learning_lst = response.split("<learning>")
    learning_lst = [learning.split("</learning>")[0] for learning in learning_lst if "</learning>" in learning]
    learning_lst = [learning for learning in learning_lst if learning]

    follow_up_questions_lst = response.split("<follow_Q>")
    follow_up_questions_lst = [follow_up_question.split("</follow_Q>")[0] for follow_up_question in follow_up_questions_lst if "</follow_Q>" in follow_up_question]
    follow_up_questions_lst = [follow_up_question for follow_up_question in follow_up_questions_lst if follow_up_question]
    
    logger.info(f"得到了了 {len(learning_lst)} 条 learning")
    logger.info(f"生成了 {len(follow_up_questions_lst)} 条 follow up questions")
    return {
        "learnings": learning_lst,
        "followUpQuestions": follow_up_questions_lst
    }

WRITE_REPORT_PROMPT = """
    对于用户提出的研究问题，使用得到的研究成果以及相关引用撰写一份关于该主题的最终报告。
    报告的格式应该严格遵循markdown格式。
    报告应该尽可能详细，包括所有研究成果。
    
    用户研究的问题为：{}
    
    以下是之前研究得到的所有成果：
    {}
    
    以下是之前研究得到的所有引用：
    {}

    根据以上内容，撰写一份关于该主题的最终报告。
"""

async def write_final_report(
    query: str,
    learnings: List[str],
    visited_urls: List[str]
) -> str:
    
    learnings_str = "\n".join(learnings)
    visited_urls_str = "\n".join(visited_urls)
    prompt = WRITE_REPORT_PROMPT.format(query, learnings_str, visited_urls_str)
    
    response = llm_query(prompt)
    response.replace("```markdown", "")
    response.replace("```", "")
    return response
    
if __name__ == "__main__":
    print(SYSTEM_PROMPT)
    