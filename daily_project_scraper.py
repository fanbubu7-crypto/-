#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日期项目检索系统 - 主程序
根据关键词自动检索和筛选项目，生成每日报告

功能:
  - 多数据源支持 (GitHub, Gitee)
  - 智能关键词匹配
  - 项目筛选和排名
  - 定时任务执行
  - 生成报告 (Markdown + JSON)
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import schedule
import time
from pathlib import Path

# ============================================================================
# 配置和初始化
# ============================================================================

from config import (
    SCRAPER_CONFIG, FILTER_CONFIG, RANKING_WEIGHTS,
    LOGGING_CONFIG, SCHEDULER_CONFIG, OUTPUT_CONFIG,
    GITHUB_TOKEN, KEYWORDS_FILE, get_github_headers
)

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    filename=LOGGING_CONFIG['file'],
    format=LOGGING_CONFIG['format'],
    encoding=LOGGING_CONFIG['encoding']
)
logger = logging.getLogger(__name__)

# ============================================================================
# 关键词匹配器
# ============================================================================

class KeywordMatcher:
    """关键词匹配器 - 从JSON文件加载关键词"""
    
    def __init__(self, keywords_file: str = KEYWORDS_FILE):
        """
        初始化关键词匹配器
        
        Args:
            keywords_file: 关键词JSON文件路径
        """
        self.keywords_file = keywords_file
        self.keywords_data = self._load_keywords()
    
    def _load_keywords(self) -> Dict:
        """加载关键词文件"""
        try:
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"关键词文件不存在: {self.keywords_file}")
            return {}
    
    def get_core_keywords(self) -> List[str]:
        """获取核心高频关键词"""
        keywords = []
        if "一、核心高频关键词" in self.keywords_data:
            for category, items in self.keywords_data["一、核心高频关键词"].items():
                if isinstance(items, list):
                    keywords.extend(items)
        return keywords
    
    def get_business_keywords(self) -> List[str]:
        """获取细分业务关键词"""
        keywords = []
        if "二、细分业务关键词" in self.keywords_data:
            for category, items in self.keywords_data["二、细分业务关键词"].items():
                if isinstance(items, list):
                    keywords.extend(items)
        return keywords
    
    def get_industry_keywords(self) -> List[str]:
        """获取行业+场景+类型关键词"""
        keywords = []
        if "三、行业+场景+类型关键词" in self.keywords_data:
            for category, items in self.keywords_data["三、行业+场景+类型关键词"].items():
                if isinstance(items, list):
                    keywords.extend(items)
        return keywords
    
    def get_location_keywords(self) -> List[str]:
        """获取地域关键词"""
        keywords = []
        if "五、地域关键词" in self.keywords_data:
            for category, items in self.keywords_data["五、地域关键词"].items():
                if isinstance(items, list):
                    keywords.extend(items)
        return keywords
    
    def get_all_keywords(self) -> List[str]:
        """获取所有关键词"""
        return (
            self.get_core_keywords() +
            self.get_business_keywords() +
            self.get_industry_keywords() +
            self.get_location_keywords()
        )

# ============================================================================
# 项目爬虫
# ============================================================================

class ProjectScraper:
    """项目爬虫 - 从GitHub和Gitee搜索项目"""
    
    def __init__(self, keyword_matcher: KeywordMatcher):
        """
        初始化项目爬虫
        
        Args:
            keyword_matcher: 关键词匹配器实例
        """
        self.keyword_matcher = keyword_matcher
        self.session = requests.Session()
    
    def scrape(self, keywords: List[str]) -> List[Dict]:
        """
        爬取项目
        
        Args:
            keywords: 关键词列表
            
        Returns:
            项目列表
        """
        projects = []
        
        # 从GitHub搜索
        github_projects = self._scrape_github(keywords)
        projects.extend(github_projects)
        logger.info(f"从GitHub获取了 {len(github_projects)} 个项目")
        
        # 从Gitee搜索
        gitee_projects = self._scrape_gitee(keywords)
        projects.extend(gitee_projects)
        logger.info(f"从Gitee获取了 {len(gitee_projects)} 个项目")
        
        return projects
    
    def _scrape_github(self, keywords: List[str]) -> List[Dict]:
        """从GitHub搜索项目"""
        projects = []
        
        for keyword in keywords:
            try:
                params = {
                    'q': keyword,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': SCRAPER_CONFIG['github']['per_page']
                }
                
                headers = get_github_headers()
                
                response = self.session.get(
                    SCRAPER_CONFIG['github']['api_url'],
                    params=params,
                    headers=headers,
                    timeout=SCRAPER_CONFIG['github']['timeout']
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for repo in data.get('items', []):
                        project = {
                            'source': 'GitHub',
                            'title': repo['name'],
                            'url': repo['html_url'],
                            'description': repo['description'],
                            'keyword': keyword,
                            'stars': repo['stargazers_count'],
                            'forks': repo['forks_count'],
                            'language': repo['language'],
                            'updated_at': repo['updated_at'],
                            'created_at': repo['created_at'],
                            'owner': repo['owner']['login']
                        }
                        projects.append(project)
                else:
                    logger.warning(f"GitHub API错误 ({keyword}): {response.status_code}")
                    
            except requests.Timeout:
                logger.error(f"GitHub API超时 ({keyword})")
            except Exception as e:
                logger.error(f"GitHub爬虫错误 ({keyword}): {e}")
        
        return projects
    
    def _scrape_gitee(self, keywords: List[str]) -> List[Dict]:
        """从Gitee搜索项目"""
        projects = []
        
        for keyword in keywords:
            try:
                params = {
                    'q': keyword,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': SCRAPER_CONFIG['gitee']['per_page']
                }
                
                response = self.session.get(
                    SCRAPER_CONFIG['gitee']['api_url'],
                    params=params,
                    timeout=SCRAPER_CONFIG['gitee']['timeout']
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Gitee返回的数据结构可能不同
                    items = data if isinstance(data, list) else data.get('data', [])
                    
                    for repo in items:
                        project = {
                            'source': 'Gitee',
                            'title': repo.get('name', ''),
                            'url': repo.get('html_url', ''),
                            'description': repo.get('description', ''),
                            'keyword': keyword,
                            'stars': repo.get('stargazers_count', 0),
                            'forks': repo.get('forks_count', 0),
                            'language': repo.get('language', ''),
                            'updated_at': repo.get('updated_at', ''),
                            'created_at': repo.get('created_at', ''),
                            'owner': repo.get('owner', {}).get('login', '') if isinstance(repo.get('owner'), dict) else ''
                        }
                        projects.append(project)
                else:
                    logger.warning(f"Gitee API错误 ({keyword}): {response.status_code}")
                    
            except requests.Timeout:
                logger.error(f"Gitee API超时 ({keyword})")
            except Exception as e:
                logger.error(f"Gitee爬虫错误 ({keyword}): {e}")
        
        return projects

# ============================================================================
# 项目筛选器
# ============================================================================

class ProjectFilter:
    """项目筛选器 - 过滤和排名项目"""
    
    def __init__(self, keyword_matcher: KeywordMatcher):
        """
        初始化项目筛选器
        
        Args:
            keyword_matcher: 关键词匹配器实例
        """
        self.keyword_matcher = keyword_matcher
    
    def filter_projects(self, projects: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        筛选项目
        
        Args:
            projects: 项目列表
            keywords: 关键词列表
            
        Returns:
            筛选后的项目列表
        """
        filtered = []
        
        for project in projects:
            # 筛选条件1: 最小星标数
            if project['stars'] < FILTER_CONFIG['min_stars']:
                continue
            
            # 筛选条件2: 最多多少天没更新
            try:
                updated_at = datetime.fromisoformat(
                    project['updated_at'].replace('Z', '+00:00')
                )
                days_old = (datetime.now(updated_at.tzinfo) - updated_at).days
                
                if days_old > FILTER_CONFIG['max_days_old']:
                    continue
            except:
                pass
            
            # 筛选条件3: 最少关键词匹配数
            keyword_matches = 0
            for keyword in keywords:
                if (keyword.lower() in project['title'].lower() or
                    (project['description'] and keyword.lower() in project['description'].lower())):
                    keyword_matches += 1
            
            if keyword_matches < FILTER_CONFIG['min_matches']:
                continue
            
            project['keyword_matches'] = keyword_matches
            filtered.append(project)
        
        logger.info(f"筛选: {len(projects)} -> {len(filtered)} 个项目")
        return filtered
    
    def rank_projects(self, projects: List[Dict]) -> List[Dict]:
        """
        排名项目
        
        Args:
            projects: 项目列表
            
        Returns:
            排名后的项目列表（按评分降序）
        """
        # 计算每个项目的评分
        for project in projects:
            # 星标热度 (0-100)
            stars_score = min(100, (project['stars'] / 100) * 100)
            
            # 更新新鲜度 (0-100)
            try:
                updated_at = datetime.fromisoformat(
                    project['updated_at'].replace('Z', '+00:00')
                )
                days_old = (datetime.now(updated_at.tzinfo) - updated_at).days
                recency_score = max(0, 100 - (days_old / 365) * 100)
            except:
                recency_score = 50
            
            # 关键词匹配度 (0-100)
            matches = project.get('keyword_matches', 1)
            matches_score = min(100, matches * 20)
            
            # 综合评分
            score = (
                stars_score * RANKING_WEIGHTS['stars'] +
                recency_score * RANKING_WEIGHTS['recency'] +
                matches_score * RANKING_WEIGHTS['matches']
            )
            
            project['score'] = score
        
        # 按评分降序排序
        ranked = sorted(projects, key=lambda x: x['score'], reverse=True)
        
        logger.info(f"排名: 完成")
        return ranked

# ============================================================================
# 报告生成器
# ============================================================================

class ReportGenerator:
    """报告生成器 - 生成Markdown和JSON报告"""
    
    def __init__(self, output_dir: str = OUTPUT_CONFIG['report_dir']):
        """
        初始化报告生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate(self, projects: List[Dict], keywords: List[str]):
        """
        生成报告
        
        Args:
            projects: 项目列表
            keywords: 搜索关键词
        """
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        if OUTPUT_CONFIG['include_markdown']:
            self._generate_markdown(projects, keywords, timestamp)
        
        if OUTPUT_CONFIG['include_json']:
            self._generate_json(projects, keywords, timestamp)
        
        logger.info(f"报告已生成到 {self.output_dir}")
    
    def _generate_markdown(self, projects: List[Dict], keywords: List[str], timestamp: str):
        """生成Markdown报告"""
        
        # 按来源分组
        by_source = {}
        for project in projects:
            source = project['source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(project)
        
        # 生成Markdown内容
        lines = [
            "# 日期项目检索报告\n",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**搜索关键词**: {', '.join(keywords)}\n",
            f"**发现项目总数**: {len(projects)}\n",
        ]
        
        for source, source_projects in by_source.items():
            lines.append(f"\n## {source} ({len(source_projects)}个项目)\n")
            
            for i, project in enumerate(source_projects, 1):
                lines.append(f"### {i}. {project['title']}\n")
                lines.append(f"- **URL**: {project['url']}\n")
                lines.append(f"- **描述**: {project['description'] or 'N/A'}\n")
                lines.append(f"- **关键词**: {project['keyword']}\n")
                lines.append(f"- **星标**: {project['stars']}\n")
                lines.append(f"- **语言**: {project['language'] or 'N/A'}\n")
                lines.append(f"- **更新时间**: {project['updated_at']}\n")
                lines.append(f"- **评分**: {project.get('score', 'N/A')}\n\n")
        
        # 保存文件
        filename = f"{self.output_dir}/report_{timestamp}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))
        
        logger.info(f"Markdown报告已保存: {filename}")
    
    def _generate_json(self, projects: List[Dict], keywords: List[str], timestamp: str):
        """生成JSON报告"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'keywords': keywords,
            'total_projects': len(projects),
            'projects': projects
        }
        
        filename = f"{self.output_dir}/report_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON报告已保存: {filename}")

# ============================================================================
# 日期调度器
# ============================================================================

class DailyScheduler:
    """日期调度器 - 管理定时任务"""
    
    def __init__(self, keyword_matcher: KeywordMatcher, 
                 scraper: ProjectScraper,
                 project_filter: ProjectFilter,
                 report_generator: ReportGenerator = None):
        """
        初始化日期调度器
        
        Args:
            keyword_matcher: 关键词匹配器
            scraper: 项目爬虫
            project_filter: 项目筛选器
            report_generator: 报告生成器
        """
        self.keyword_matcher = keyword_matcher
        self.scraper = scraper
        self.project_filter = project_filter
        self.report_generator = report_generator or ReportGenerator()
    
    def daily_task(self, keywords: List[str], output_dir: str = OUTPUT_CONFIG['report_dir']):
        """
        执行每日任务
        
        Args:
            keywords: 关键词列表
            output_dir: 输出目录
        """
        logger.info("=" * 80)
        logger.info("开始执行每日项目检索任务")
        logger.info("=" * 80)
        
        try:
            # 1. 爬取项目
            logger.info(f"正在爬取项目，关键词: {keywords}")
            projects = self.scraper.scrape(keywords)
            logger.info(f"共爬取 {len(projects)} 个项目")
            
            if not projects:
                logger.warning("未找到任何项目")
                return
            
            # 2. 筛选项目
            logger.info("正在筛选项目...")
            filtered = self.project_filter.filter_projects(projects, keywords)
            
            if not filtered:
                logger.warning("筛选后未找到任何项目")
                return
            
            # 3. 排名项目
            logger.info("正在排名项目...")
            ranked = self.project_filter.rank_projects(filtered)
            
            # 4. 生成报告
            logger.info("正在生成报告...")
            self.report_generator.generate(ranked, keywords)
            
            logger.info("=" * 80)
            logger.info("每日任务完成!")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"执行任务出错: {e}", exc_info=True)
    
    def schedule_daily(self, keywords: List[str], run_time: str = SCHEDULER_CONFIG['run_time']):
        """
        安排每日定时任务
        
        Args:
            keywords: 关键词列表
            run_time: 运行时间 (HH:MM格式)
        """
        logger.info(f"安排每日定时任务，运行时间: {run_time}")
        
        schedule.every().day.at(run_time).do(self.daily_task, keywords=keywords)
        
        logger.info("定时任务已启动，按 Ctrl+C 停止")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("定时任务已停止")

# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    
    logger.info("初始化系统...")
    
    # 初始化各个组件
    keyword_matcher = KeywordMatcher(KEYWORDS_FILE)
    scraper = ProjectScraper(keyword_matcher)
    project_filter = ProjectFilter(keyword_matcher)
    report_generator = ReportGenerator()
    scheduler = DailyScheduler(keyword_matcher, scraper, project_filter, report_generator)
    
    # 获取前5个核心关键词
    core_keywords = keyword_matcher.get_core_keywords()[:5]
    
    # 立即执行一次
    print("\n" + "=" * 80)
    print("日期项目检索系统")
    print("=" * 80 + "\n")
    print(f"搜索关键词: {core_keywords}\n")
    
    scheduler.daily_task(core_keywords)
    
    # 如果启用了定时任务，继续运行
    # 注意: 下面的代码会阻塞程序，定时执行任务
    # 如需启用，请取消注释
    
    # if SCHEDULER_CONFIG['enabled']:
    #     scheduler.schedule_daily(core_keywords)

if __name__ == '__main__':
    main()
