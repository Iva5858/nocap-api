from crewai import Agent, Crew, Process, Task
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain.tools import Tool
import os
import yaml
from datetime import datetime
from dotenv import load_dotenv
import time
import re
import requests
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

class InstagramFactCheckCrew:
	def __init__(self):
		self.tasks_config = self.load_config('tasks')
		self.agents_config = self.load_config('agents')
		
	def load_config(self, config_type):
		# Get the directory where the current file (crew.py) is located
		current_dir = os.path.dirname(os.path.abspath(__file__))
		
		# Load config
		config_path = os.path.join(current_dir, 'config', f'{config_type}.yaml')
		with open(config_path, 'r') as f:
			return yaml.safe_load(f)

	def create_search_tool(self):
		"""Create a search tool with basic configuration"""
		wrapper = DuckDuckGoSearchAPIWrapper()
		return DuckDuckGoSearchRun(api_wrapper=wrapper)

	def create_agents(self):
		# Create a basic search tool
		search_tool = self.create_search_tool()
		
		# Initialize agents with the search tool
		self.fact_checker = Agent(
			role=self.agents_config['fact_checker']['role'],
			goal=self.agents_config['fact_checker']['goal'],
			backstory=self.agents_config['fact_checker']['backstory'],
			tools=[search_tool],
			verbose=True,
			allow_delegation=False
		)
		
		self.analysis_writer = Agent(
			role=self.agents_config['analysis_writer']['role'],
			goal=self.agents_config['analysis_writer']['goal'],
			backstory=self.agents_config['analysis_writer']['backstory'],
			verbose=True,
			allow_delegation=False
		)
		
		self.format_checker = Agent(
			role=self.agents_config['format_checker']['role'],
			goal=self.agents_config['format_checker']['goal'],
			backstory=self.agents_config['format_checker']['backstory'],
			verbose=True,
			allow_delegation=False
		)

	def create_tasks(self, post_data: dict):
		verify_config = self.tasks_config['verify_content']
		analysis_config = self.tasks_config['create_analysis_report']
		validate_config = self.tasks_config['validate_format']
		
		verify_description = verify_config['description'].format(
			username=post_data['username'],
			description=post_data['description'],
			post_url=post_data['post_url']
		)
		
		self.verify_task = Task(
			description=verify_description,
			expected_output=verify_config['expected_output'],
			agent=self.fact_checker
		)
		
		self.analysis_task = Task(
			description=analysis_config['description'],
			expected_output=analysis_config['expected_output'],
			agent=self.analysis_writer
		)
		
		self.validate_task = Task(
			description=validate_config['description'],
			expected_output=validate_config['expected_output'],
			agent=self.format_checker
		)

	def validate_url(self, url):
		"""Validate if a URL is well-formed and accessible"""
		try:
			# Check if URL is well-formed
			result = urlparse(url)
			if not all([result.scheme, result.netloc]):
				return False
			
			# Check if URL starts with http:// or https://
			if not url.startswith(('http://', 'https://')):
				return False
			
			# Try to access the URL with a timeout
			response = requests.head(url, timeout=5, allow_redirects=True)
			return response.status_code == 200
		except:
			return False

	def validate_content(self, content):
		"""Validate content has proper URLs"""
		# Find all URLs in the content
		urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
		
		if not urls:
			return False
		
		# Validate each URL
		valid_urls = [url for url in urls if self.validate_url(url)]
		return len(valid_urls) >= 2

	def run(self, post_data: dict):
		max_retries = 3
		retry_delay = 2
		
		for attempt in range(max_retries):
			try:
				self.create_agents()
				self.create_tasks(post_data)
				
				crew = Crew(
					agents=[self.fact_checker, self.analysis_writer],
					tasks=[self.verify_task, self.analysis_task],
					process=Process.sequential,
					verbose=True
				)
				
				result = str(crew.kickoff())
				
				# If result is too long, request a shorter version
				while len(result) > 850:
					self.analysis_task = Task(
						description=f"""
						The previous analysis was too long ({len(result)} characters).
						Rewrite it to be under 850 characters total while maintaining:
						1. The main claim
						2. Key verification points with source citations
						3. Bias and reliability scores
						
						Use the same format but be more concise.
						Remember to cite sources by organization name and date.
						""",
						expected_output="A shorter analysis under 850 characters",
						agent=self.analysis_writer
					)
					
					crew = Crew(
						agents=[self.analysis_writer],
						tasks=[self.analysis_task],
						process=Process.sequential,
						verbose=True
					)
					
					result = str(crew.kickoff())
					
					if len(result) <= 850:
						break
				
				return {
					"message": [
						{
							"content": result,
							"timestamp": datetime.now().isoformat()
						}
					]
				}
				
			except Exception as e:
				if "Ratelimit" in str(e) and attempt < max_retries - 1:
					wait_time = retry_delay * (2 ** attempt)
					time.sleep(wait_time)
					continue
					
				return {
					"message": [
						{
							"error": str(e),
							"status": "failed",
							"timestamp": datetime.now().isoformat()
						}
					]
				}
		
		return {
			"message": [
				{
					"error": "Maximum retries reached. Service temporarily unavailable.",
					"status": "failed",
					"timestamp": datetime.now().isoformat()
				}
			]
		}
	

