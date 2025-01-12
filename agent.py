import json
from datetime import datetime
from typing import List, Dict, Any
import os
import logging
from dataclasses import dataclass
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.llms.ollama import Ollama
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Competitor:
    name: str
    website: str
    social_media: Dict[str, str]

class CompetitorDatabase:
    def __init__(self, storage_dir: str = "competitor_data"):
        self.storage_dir = storage_dir
        self.llm = Ollama(
            model="your-model",
            base_url="http://localhost:11434",
            request_timeout=60.0
        )
        self.embed_model = OllamaEmbedding(
            model_name="your-model",
            base_url="http://localhost:11434",
            ollama_additional_kwargs={"mirostat": 0}
        )
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = 512
        os.makedirs(storage_dir, exist_ok=True)

    def test_embeddings(self):
        try:
            test_texts = [
                "Testing competitor analysis embeddings",
                "Another test passage for embeddings"
            ]
            batch_embeddings = self.embed_model.get_text_embedding_batch(
                test_texts, 
                show_progress=True
            )
            logger.info(f"Successfully generated batch embeddings: {len(batch_embeddings)} embeddings")
            query = "What are the competitor's features?"
            query_embedding = self.embed_model.get_query_embedding(query)
            logger.info(f"Successfully generated query embedding of length: {len(query_embedding)}")
            return True
        except Exception as e:
            logger.error(f"Error testing embeddings: {str(e)}")
            return False

    def store_competitor_data(self, competitor_name: str, content: str, date: str):
        try:
            doc = Document(
                text=content,
                metadata={
                    "competitor": competitor_name,
                    "date": date
                }
            )
            competitor_dir = os.path.join(self.storage_dir, competitor_name)
            os.makedirs(competitor_dir, exist_ok=True)
            try:
                index = load_index_from_storage(
                    StorageContext.from_defaults(persist_dir=competitor_dir)
                )
            except:
                index = VectorStoreIndex.from_documents([doc])
            index.insert(doc)
            index.storage_context.persist(persist_dir=competitor_dir)
            logger.info(f"Stored data for {competitor_name}")
            return True
        except Exception as e:
            logger.error(f"Error storing competitor data: {str(e)}")
            return False

    def query_competitor_history(self, competitor_name: str, query: str) -> str:
        try:
            competitor_dir = os.path.join(self.storage_dir, competitor_name)
            if not os.path.exists(competitor_dir):
                return ""
            index = load_index_from_storage(
                StorageContext.from_defaults(persist_dir=competitor_dir)
            )
            query_engine = index.as_query_engine()
            response = query_engine.query(query)
            return str(response)
        except Exception as e:
            logger.error(f"Error querying competitor history: {str(e)}")
            return ""

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def scrape_website(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        for script in soup(["script", "style"]):
                            script.decompose()
                        text = soup.get_text(separator='\n', strip=True)
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        return text
                    else:
                        logger.error(f"Error scraping website {url}: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"Exception in scrape_website: {str(e)}")
            return ""

class CompetitiveAnalysisAgent:
    def __init__(self):
        self.web_scraper = WebScraper()
        self.competitor_db = CompetitorDatabase()

    def load_competitors(self, file_path: str) -> List[Competitor]:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                competitors_data = data.get('competitors', [])
                return [Competitor(**comp) for comp in competitors_data]
        except Exception as e:
            logger.error(f"Error loading competitors: {str(e)}")
            return []

    async def analyze_competitor_website(self, competitor: Competitor) -> Dict[str, Any]:
        current_content = await self.web_scraper.scrape_website(competitor.website)
        today = datetime.now().strftime("%Y-%m-%d")
        self.competitor_db.store_competitor_data(competitor.name, current_content, today)

        historical_query = """
        What are the main changes in terms of:
        1. Pricing
        2. Products
        3. Partnerships
        4. Funding
        5. Positioning
        Compare with historical data and identify significant changes.
        """
        historical_analysis = self.competitor_db.query_competitor_history(
            competitor.name,
            historical_query
        )
        current_analysis = self.competitor_db.query_competitor_history(
            competitor.name,
            """
            Analyze the latest content and identify:
            1. Current pricing information
            2. Product offerings
            3. Recent partnerships
            4. Funding news
            5. Market positioning
            Provide the analysis in JSON format.
            """
        )
        try:
            analysis_result = json.loads(current_analysis)
        except json.JSONDecodeError:
            analysis_result = {
                "pricing_changes": [],
                "product_launches": [],
                "partnerships": [],
                "funding": [],
                "positioning_changes": []
            }
        analysis_result["historical_changes"] = historical_analysis
        return analysis_result

    async def generate_weekly_report(self, competitors: List[Competitor]) -> str:
        all_analyses = []
        for competitor in competitors:
            analysis = await self.analyze_competitor_website(competitor)
            all_analyses.append({
                "competitor": competitor.name,
                "analysis": analysis
            })
        report_prompt = f"""
        Generate a weekly competitive analysis report based on the following data:
        {json.dumps(all_analyses, indent=2)}
        
        Format the report with:
        1. Executive Summary
        2. Key Findings by Competitor
        3. Market Trends
        4. Historical Changes
        5. Recommendations
        
        Focus on significant changes and their market impact.
        """
        query_engine = self.competitor_db.llm
        report = query_engine.complete(report_prompt)
        return str(report)

    def save_report(self, report: str, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"competitive_analysis_report_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {filepath}")
        return filepath

async def main():
    agent = CompetitiveAnalysisAgent()
    competitors = agent.load_competitors("competitors.json")
    if not competitors:
        logger.error("No competitors loaded. Please check your competitors.json file.")
        return
    report = await agent.generate_weekly_report(competitors)
    output_dir = "reports"
    saved_path = agent.save_report(report, output_dir)
    logger.info(f"Weekly competitive analysis completed. Report saved to: {saved_path}")

if __name__ == "__main__":
    asyncio.run(main())