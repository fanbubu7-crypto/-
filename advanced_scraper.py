#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级项目爬虫 - 支持更多数据源和高级筛选功能
"""

import json
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import aiohttp
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class AdvancedProjectScraper:
    """高级爬虫 - 支持多个数据源"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_github_advanced(self, 
                                     keywords: List[str],
                                     language: str = None,
                                     min_stars: int = 5,
                                     sort: str = "stars") -> List[Dict]:
        """
        高级GitHub爬虫 - 支持异步请求
        
        Args:
            keywords: 关键词列表
            language: 编程语言筛选
            min_stars: 最小星标数
            sort: 排序方式 (stars, forks, updated)
            
        Returns:
            项目列表
        """
        projects = []
        
        for keyword in keywords:
            query = f"{keyword} stars:>{min_stars}"
            if language:
                query += f" language:{language}"
            
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": sort,
                "order": "desc",
                "per_page": 100,
                "page": 1
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for repo in data.get('items', []):
                            project = {
                                'source': 'GitHub',
                                'id': repo['id'],
                                'name': repo['name'],
                                'url': repo['html_url'],
                                'description': repo['description'],
                                'owner': repo['owner']['login'],
                                'stars': repo['stargazers_count'],
                                'forks': repo['forks_count'],
                                'watchers': repo['watchers_count'],
                                'language': repo['language'],
                                'topics': repo.get('topics', []),
                                'created_at': repo['created_at'],
                                'updated_at': repo['updated_at'],
                                'homepage': repo['homepage'],
                                'license': repo['license'],
                                'is_fork': repo['fork'],
                                'open_issues': repo['open_issues_count']
                            }
                            projects.append(project)
                    else:
                        logger.error(f"GitHub API错误: {response.status}")
                        
            except asyncio.TimeoutError:
                logger.error(f"GitHub API超时: {keyword}")
            except Exception as e:
                logger.error(f"GitHub爬虫错误: {e}")
        
        return projects
    
    async def scrape_gitee_advanced(self, 
                                    keywords: List[str],
                                    min_stars: int = 5) -> List[Dict]:
        """
        高级Gitee爬虫 - 支持异步请求
        
        Args:
            keywords: 关键词列表
            min_stars: 最小星标数
            
        Returns:
            项目列表
        """
        projects = []
        
        for keyword in keywords:
            url = "https://gitee.com/api/v5/search/repositories"
            params = {
                "q": keyword,
                "sort": "stars",
                "order": "desc",
                "per_page": 100,
                "page": 1
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for repo in data.get('data', []):
                            project = {
                                'source': 'Gitee',
                                'id': repo['id'],
                                'name': repo['name'],
                                'url': repo['html_url'],
                                'description': repo['description'],
                                'owner': repo['owner']['login'],
                                'stars': repo['stargazers_count'],
                                'forks': repo['forks_count'],
                                'watchers': repo['watchers_count'],
                                'language': repo['language'],
                                'topics': repo.get('topics', []),
                                'created_at': repo['created_at'],
                                'updated_at': repo['updated_at'],
                                'homepage': repo['homepage'],
                                'license': repo.get('license', {}).get('name'),
                                'is_fork': repo['fork'],
                                'open_issues': repo['issues_count']
                            }
                            projects.append(project)
                    else:
                        logger.error(f"Gitee API错误: {response.status}")
                        
            except asyncio.TimeoutError:
                logger.error(f"Gitee API超时: {keyword}")
            except Exception as e:
                logger.error(f"Gitee爬虫错误: {e}")
        
        return projects
    
    async def scrape_gitlab(self, 
                           keywords: List[str],
                           gitlab_url: str = "https://gitlab.com",
                           min_stars: int = 5) -> List[Dict]:
        """
        GitLab爬虫 - 支持自建GitLab实例
        
        Args:
            keywords: 关键词列表
            gitlab_url: GitLab服务器URL
            min_stars: 最小星标数
            
        Returns:
            项目列表
        """
        projects = []
        
        for keyword in keywords:
            url = f"{gitlab_url}/api/v4/projects"
            params = {
                "search": keyword,
                "simple": False,
                "per_page": 100,
                "page": 1
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for repo in data:
                            if repo.get('star_count', 0) < min_stars:
                                continue
                            
                            project = {
                                'source': 'GitLab',
                                'id': repo['id'],
                                'name': repo['name'],
                                'url': repo['web_url'],
                                'description': repo['description'],
                                'owner': repo['owner']['username'],
                                'stars': repo.get('star_count', 0),
                                'forks': repo.get('forks_count', 0),
                                'watchers': repo.get('star_count', 0),
                                'language': None,  # GitLab不提供
                                'topics': repo.get('topics', []),
                                'created_at': repo['created_at'],
                                'updated_at': repo['last_activity_at'],
                                'homepage': repo.get('web_url'),
                                'license': None,
                                'is_fork': repo.get('forked_from_project') is not None,
                                'open_issues': repo.get('open_issues_count', 0)
                            }
                            projects.append(project)
                    else:
                        logger.error(f"GitLab API错误: {response.status}")
                        
            except Exception as e:
                logger.error(f"GitLab爬虫错误: {e}")
        
        return projects


class ProjectAnalyzer:
    """项目分析器"""
    
    @staticmethod
    def analyze_project_health(project: Dict) -> Dict:
        """
        分析项目健康度
        
        Args:
            project: 项目信息
            
        Returns:
            健康度分析结果
        """
        health_score = 0
        details = {}
        
        # 1. 活跃度评分
        try:
            updated_at = datetime.fromisoformat(
                project['updated_at'].replace('Z', '+00:00')
            )
            days_since_update = (datetime.now(updated_at.tzinfo) - updated_at).days
            
            if days_since_update < 7:
                activity_score = 100
            elif days_since_update < 30:
                activity_score = 80
            elif days_since_update < 90:
                activity_score = 60
            elif days_since_update < 180:
                activity_score = 40
            else:
                activity_score = 20
            
            details['活跃度'] = activity_score
            health_score += activity_score * 0.3
            
        except Exception as e:
            logger.error(f"活跃度分析错误: {e}")
            details['活跃度'] = 0
        
        # 2. 热度评分
        stars = project.get('stars', 0)
        if stars > 10000:
            popularity_score = 100
        elif stars > 1000:
            popularity_score = 80
        elif stars > 100:
            popularity_score = 60
        elif stars > 10:
            popularity_score = 40
        else:
            popularity_score = 20
        
        details['热度'] = popularity_score
        health_score += popularity_score * 0.3
        
        # 3. 参与度评分
        forks = project.get('forks', 0)
        watchers = project.get('watchers', 0)
        
        participation = forks + watchers
        if participation > stars * 0.1:
            participation_score = 100
        elif participation > stars * 0.05:
            participation_score = 80
        elif participation > 10:
            participation_score = 60
        else:
            participation_score = 40
        
        details['参与度'] = participation_score
        health_score += participation_score * 0.2
        
        # 4. 维护度评分
        open_issues = project.get('open_issues', 0)
        
        if open_issues == 0:
            maintenance_score = 100
        elif open_issues < 10:
            maintenance_score = 80
        elif open_issues < 50:
            maintenance_score = 60
        else:
            maintenance_score = 40
        
        details['维护度'] = maintenance_score
        health_score += maintenance_score * 0.2
        
        # 5. 是否Fork评分
        if not project.get('is_fork', False):
            fork_score = 100
        else:
            fork_score = 50
        
        details['独立性'] = fork_score
        
        return {
            'overall_score': round(health_score, 2),
            'scores': details,
            'rating': classify_health(health_score)
        }


def classify_health(score: float) -> str:
    """
    根据分数分类健康度
    
    Args:
        score: 分数
        
    Returns:
        分类（优秀/良好/一般/较差）
    """
    if score >= 80:
        return '⭐ 优秀'
    elif score >= 60:
        return '✨ 良好'
    elif score >= 40:
        return '👍 一般'
    else:
        return '⚠️  较差'


class ProjectComparator:
    """项目对比分析器"""
    
    @staticmethod
    def compare_projects(project_list: List[Dict]) -> Dict:
        """
        对比项目列表
        
        Args:
            project_list: 项目列表
            
        Returns:
            对比分析结果
        """
        analyzer = ProjectAnalyzer()
        
        # 为每个项目分析健康度
        projects_with_health = []
        for project in project_list:
            health = analyzer.analyze_project_health(project)
            projects_with_health.append({
                **project,
                'health': health
            })
        
        # 统计信息
        stats = {
            'total_projects': len(project_list),
            'by_source': {},
            'by_language': {},
            'average_stars': 0,
            'average_forks': 0,
            'average_health_score': 0,
            'top_projects': [],
            'distribution': {
                '优秀': 0,
                '良好': 0,
                '一般': 0,
                '较差': 0
            }
        }
        
        # 按来源分类
        for project in projects_with_health:
            source = project['source']
            if source not in stats['by_source']:
                stats['by_source'][source] = 0
            stats['by_source'][source] += 1
            
            # 按语言分类
            language = project.get('language', 'Unknown')
            if language not in stats['by_language']:
                stats['by_language'][language] = 0
            stats['by_language'][language] += 1
            
            # 统计分数
            stats['average_stars'] += project.get('stars', 0)
            stats['average_forks'] += project.get('forks', 0)
            stats['average_health_score'] += project['health']['overall_score']
            
            # 健康度分布
            rating = project['health']['rating'].split()[1]
            if rating == '优秀':
                stats['distribution']['优秀'] += 1
            elif rating == '良好':
                stats['distribution']['良好'] += 1
            elif rating == '一般':
                stats['distribution']['一般'] += 1
            else:
                stats['distribution']['较差'] += 1
        
        # 计算平均值
        if project_list:
            stats['average_stars'] = round(stats['average_stars'] / len(project_list), 2)
            stats['average_forks'] = round(stats['average_forks'] / len(project_list), 2)
            stats['average_health_score'] = round(
                stats['average_health_score'] / len(project_list), 2
            )
        
        # 获取Top 10项目
        sorted_projects = sorted(
            projects_with_health,
            key=lambda x: x['health']['overall_score'],
            reverse=True
        )[:10]
        
        stats['top_projects'] = [
            {
                'name': p['name'],
                'url': p['url'],
                'health_score': p['health']['overall_score'],
                'rating': p['health']['rating'],
                'stars': p['stars']
            }
            for p in sorted_projects
        ]
        
        return stats


# 使用示例
async def main():
    """主函数 - 示例用法"""
    
    keywords = ['Python', 'JavaScript', 'Go']
    
    async with AdvancedProjectScraper() as scraper:
        # 爬取项目
        github_projects = await scraper.scrape_github_advanced(keywords)
        gitee_projects = await scraper.scrape_gitee_advanced(keywords)
        
        all_projects = github_projects + gitee_projects
        
        # 分析项目
        comparator = ProjectComparator()
        comparison_result = comparator.compare_projects(all_projects)
        
        # 输出结果
        print(json.dumps(comparison_result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
