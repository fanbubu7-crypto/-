#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例 - 展示系统的各种使用方式
"""

from daily_project_scraper import (
    KeywordMatcher, ProjectScraper, ProjectFilter, 
    ReportGenerator, DailyScheduler
)

# ============================================================================
# 示例1: 基础使用 - 一次性搜索
# ============================================================================

def example_basic_search():
    """示例1: 基础使用 - 一次性搜索"""
    
    print("\n" + "="*80)
    print("示例1: 基础使用 - 一次性搜索")
    print("="*80)
    
    # 初始化组件
    keyword_matcher = KeywordMatcher('keywords.json')
    scraper = ProjectScraper(keyword_matcher)
    project_filter = ProjectFilter(keyword_matcher)
    scheduler = DailyScheduler(keyword_matcher, scraper, project_filter)
    
    # 自定义关键词
    keywords = ['Python', '机器学习']
    
    # 执行任务
    scheduler.daily_task(keywords)

# ============================================================================
# 示例2: 获取不同类型的关键词
# ============================================================================

def example_get_keywords():
    """示例2: 获取不同类型的关键词"""
    
    print("\n" + "="*80)
    print("示例2: 获取不同类型的关键词")
    print("="*80)
    
    keyword_matcher = KeywordMatcher('keywords.json')
    
    # 获取核心关键词
    core_keywords = keyword_matcher.get_core_keywords()
    print(f"\n核心高频关键词 ({len(core_keywords)}个):")
    print(core_keywords[:10])  # 显示前10个
    
    # 获取业务关键词
    business_keywords = keyword_matcher.get_business_keywords()
    print(f"\n细分业务关键词 ({len(business_keywords)}个):")
    print(business_keywords)
    
    # 获取行业关键词
    industry_keywords = keyword_matcher.get_industry_keywords()
    print(f"\n行业+场景+类型关键词 ({len(industry_keywords)}个):")
    print(industry_keywords[:10])  # 显示前10个
    
    # 获取地域关键词
    location_keywords = keyword_matcher.get_location_keywords()
    print(f"\n地域关键词 ({len(location_keywords)}个):")
    print(location_keywords[:10])  # 显示前10个

# ============================================================================
# 示例3: 自定义筛选条件
# ============================================================================

def example_custom_filtering():
    """示例3: 自定义筛选条件"""
    
    print("\n" + "="*80)
    print("示例3: 自定义筛选条件")
    print("="*80)
    
    from config import FILTER_CONFIG
    
    print("\n当前筛选配置:")
    print(f"  - 最小星标数: {FILTER_CONFIG['min_stars']}")
    print(f"  - 最少关键词匹配数: {FILTER_CONFIG['min_matches']}")
    print(f"  - 最多多少天没更新: {FILTER_CONFIG['max_days_old']} 天")
    
    print("\n提示: 要修改筛选条件，编辑 config.py 文件中的 FILTER_CONFIG")

# ============================================================================
# 示例4: 自定义排名权重
# ============================================================================

def example_custom_ranking():
    """示例4: 自定义排名权重"""
    
    print("\n" + "="*80)
    print("示例4: 自定义排名权重")
    print("="*80)
    
    from config import RANKING_WEIGHTS
    
    print("\n当前排名权重:")
    print(f"  - 星标权重: {RANKING_WEIGHTS['stars']} (50%)")
    print(f"  - 更新时间权重: {RANKING_WEIGHTS['recency']} (30%)")
    print(f"  - 关键词匹配度权重: {RANKING_WEIGHTS['matches']} (20%)")
    
    print("\n排名公式:")
    print("  评分 = 50% × 星标热度 + 30% × 更新新鲜度 + 20% × 关键词匹配度")
    
    print("\n提示: 要修改排名权重，编辑 config.py 文件中的 RANKING_WEIGHTS")

# ============================================================================
# 示例5: 高级爬虫 - 异步爬取
# ============================================================================

def example_advanced_scraper():
    """示例5: 高级爬虫 - 异步爬取"""
    
    print("\n" + "="*80)
    print("示例5: 高级爬虫 - 异步爬取")
    print("="*80)
    
    import asyncio
    from advanced_scraper import AdvancedProjectScraper
    
    async def run():
        keywords = ['Python', 'JavaScript']
        
        async with AdvancedProjectScraper() as scraper:
            # 异步爬取GitHub项目
            github_projects = await scraper.scrape_github_advanced(keywords)
            print(f"\n从GitHub获取了 {len(github_projects)} 个项目")
            
            # 异步爬取Gitee项目
            gitee_projects = await scraper.scrape_gitee_advanced(keywords)
            print(f"从Gitee获取了 {len(gitee_projects)} 个项目")
            
            # 显示前3个项目
            all_projects = github_projects + gitee_projects
            print(f"\n前3个项目:")
            for project in all_projects[:3]:
                print(f"  - {project['name']} ({project['source']}): {project['stars']} ⭐")
    
    # 运行异步任务
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"错误: {e}")

# ============================================================================
# 示例6: 项目分析 - 健康度评分
# ============================================================================

def example_project_analysis():
    """示例6: 项目分析 - 健康度评分"""
    
    print("\n" + "="*80)
    print("示例6: 项目分析 - 健康度评分")
    print("="*80)
    
    from advanced_scraper import ProjectAnalyzer
    
    # 示例项目数据
    project = {
        'name': 'awesome-project',
        'stars': 1500,
        'forks': 200,
        'watchers': 1500,
        'open_issues': 5,
        'is_fork': False,
        'updated_at': '2026-04-28T15:30:00Z'
    }
    
    analyzer = ProjectAnalyzer()
    health = analyzer.analyze_project_health(project)
    
    print(f"\n项目: {project['name']}")
    print(f"健康度评分:")
    print(f"  - 总分: {health['overall_score']}/100")
    print(f"  - 等级: {health['rating']}")
    print(f"  - 各维度分数:")
    for dimension, score in health['scores'].items():
        print(f"    * {dimension}: {score}/100")

# ============================================================================
# 示例7: 项目对比分析
# ============================================================================

def example_project_comparison():
    """示例7: 项目对比分析"""
    
    print("\n" + "="*80)
    print("示例7: 项目对比分析")
    print("="*80)
    
    from advanced_scraper import ProjectComparator
    
    # 示例项目列表
    projects = [
        {
            'name': 'project-1',
            'source': 'GitHub',
            'stars': 1500,
            'forks': 200,
            'watchers': 1500,
            'open_issues': 5,
            'is_fork': False,
            'updated_at': '2026-04-28T15:30:00Z',
            'language': 'Python'
        },
        {
            'name': 'project-2',
            'source': 'Gitee',
            'stars': 800,
            'forks': 100,
            'watchers': 800,
            'open_issues': 10,
            'is_fork': False,
            'updated_at': '2026-04-27T10:20:00Z',
            'language': 'JavaScript'
        }
    ]
    
    comparator = ProjectComparator()
    comparison = comparator.compare_projects(projects)
    
    print(f"\n对比统计:")
    print(f"  - 总项目数: {comparison['total_projects']}")
    print(f"  - 平均星标: {comparison['average_stars']}")
    print(f"  - 平均健康度: {comparison['average_health_score']}/100")
    print(f"  - 按来源分布: {comparison['by_source']}")
    print(f"  - 健康度分布:")
    for rating, count in comparison['distribution'].items():
        print(f"    * {rating}: {count} 个")

# ============================================================================
# 示例8: 定时任务 (每日09:00执行)
# ============================================================================

def example_scheduled_task():
    """���例8: 定时任务 (每日09:00执行)"""
    
    print("\n" + "="*80)
    print("示例8: 定时任务 (每日09:00执行)")
    print("="*80)
    
    print("\n代码示例:")
    print("""
from daily_project_scraper import *

keyword_matcher = KeywordMatcher('keywords.json')
scraper = ProjectScraper(keyword_matcher)
project_filter = ProjectFilter(keyword_matcher)
scheduler = DailyScheduler(keyword_matcher, scraper, project_filter)

# 每日09:00执行
keywords = ['Python', '机器学习']
scheduler.schedule_daily(keywords, run_time="09:00")

# 程序会持续运行，每天09:00自动执行
# 按 Ctrl+C 停止
    """)
    
    print("提示: 要启用定时任务，修改 daily_project_scraper.py 中的 main() 函数")

# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数 - 选择要运行的示例"""
    
    print("""
    ╔═════════════════════════════════════════════════════════════════════��════╗
    ║           日期项目检索系统 - 使用示例                                     ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    
    请选择要运行的示例:
    
    1. 基础使用 - 一次性搜索
    2. 获取不同类型的关键词
    3. 自定义筛选条件
    4. 自定义排名权重
    5. 高级爬虫 - 异步爬取
    6. 项目分析 - 健康度评分
    7. 项目对比分析
    8. 定时任务 (每日09:00执行)
    
    按 Ctrl+C 退出
    """)
    
    while True:
        try:
            choice = input("\n请输入选项 (1-8): ").strip()
            
            if choice == '1':
                example_basic_search()
            elif choice == '2':
                example_get_keywords()
            elif choice == '3':
                example_custom_filtering()
            elif choice == '4':
                example_custom_ranking()
            elif choice == '5':
                example_advanced_scraper()
            elif choice == '6':
                example_project_analysis()
            elif choice == '7':
                example_project_comparison()
            elif choice == '8':
                example_scheduled_task()
            else:
                print("无效的选项，请重试")
                
        except KeyboardInterrupt:
            print("\n\n已退出")
            break
        except Exception as e:
            print(f"错误: {e}")

if __name__ == '__main__':
    main()
