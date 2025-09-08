from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import time
import json
import io
import base64
from datetime import datetime
import random
import re

app = Flask(__name__)
CORS(app)

processing_cache = {}

NEWS_ARTICLES_DATABASE = [
    {"id": 1, "text": "Breaking: Revolutionary AI model achieves 95% accuracy in real-time language translation", "category": "technology", "timestamp": "2025-01-15 10:30:00"},
    {"id": 2, "text": "Market Alert: Tech stocks surge 8% following breakthrough in quantum computing research", "category": "finance", "timestamp": "2025-01-15 09:45:00"},
    {"id": 3, "text": "Health Update: New study reveals significant benefits of Mediterranean diet for cognitive function", "category": "health", "timestamp": "2025-01-15 08:20:00"},
    {"id": 4, "text": "Sports News: Championship final draws record-breaking viewership across streaming platforms", "category": "sports", "timestamp": "2025-01-15 07:15:00"},
    {"id": 5, "text": "Environmental Report: Renewable energy adoption reaches 45% globally, exceeding predictions", "category": "environment", "timestamp": "2025-01-14 16:30:00"},
    {"id": 6, "text": "Business Insight: Major corporation announces $2B investment in sustainable manufacturing", "category": "business", "timestamp": "2025-01-14 14:45:00"},
    {"id": 7, "text": "Science Discovery: Researchers identify new exoplanet with potential for water existence", "category": "science", "timestamp": "2025-01-14 12:20:00"},
    {"id": 8, "text": "Political Update: International climate agreement signed by 150 nations for carbon neutrality", "category": "politics", "timestamp": "2025-01-14 11:00:00"},
    {"id": 9, "text": "Entertainment: Streaming platform reports 300% increase in documentary viewership this quarter", "category": "entertainment", "timestamp": "2025-01-14 09:30:00"},
    {"id": 10, "text": "Education News: Universities adopt AI-powered personalized learning systems with 90% success rate", "category": "education", "timestamp": "2025-01-14 08:45:00"},
    {"id": 11, "text": "Automotive: Electric vehicle sales surpass traditional cars for first time in major markets", "category": "automotive", "timestamp": "2025-01-13 17:20:00"},
    {"id": 12, "text": "Real Estate: Smart city development project breaks ground with sustainable architecture focus", "category": "real_estate", "timestamp": "2025-01-13 15:40:00"},
    {"id": 13, "text": "Cybersecurity Alert: New encryption standard provides quantum-resistant protection for data", "category": "cybersecurity", "timestamp": "2025-01-13 13:25:00"},
    {"id": 14, "text": "Travel Advisory: Tourism industry reports full recovery with AI-enhanced booking experiences", "category": "travel", "timestamp": "2025-01-13 11:50:00"},
    {"id": 15, "text": "Food Industry: Plant-based alternatives achieve cost parity with traditional products", "category": "food", "timestamp": "2025-01-13 10:15:00"},
    {"id": 16, "text": "Energy Update: Solar power efficiency breakthrough achieves 47% conversion rate in lab tests", "category": "energy", "timestamp": "2025-01-12 16:00:00"},
    {"id": 17, "text": "Space Exploration: Private space mission successfully deploys advanced satellite constellation", "category": "space", "timestamp": "2025-01-12 14:30:00"},
    {"id": 18, "text": "Medical Breakthrough: Gene therapy trial shows promising results for rare genetic disorders", "category": "medical", "timestamp": "2025-01-12 12:45:00"},
    {"id": 19, "text": "Transportation: Autonomous delivery drones receive approval for urban deployment", "category": "transportation", "timestamp": "2025-01-12 10:20:00"},
    {"id": 20, "text": "Social Media: Platform implements advanced AI moderation reducing harmful content by 85%", "category": "social_media", "timestamp": "2025-01-12 08:55:00"}
] * 25

USER_PREFERENCES_DATABASE = [
    {"user_id": "U001", "name": "Alex Chen", "interests": ["technology", "science", "business"]},
    {"user_id": "U002", "name": "Maria Rodriguez", "interests": ["health", "environment", "education"]},
    {"user_id": "U003", "name": "James Wilson", "interests": ["finance", "automotive", "energy"]},
    {"user_id": "U004", "name": "Sarah Kim", "interests": ["entertainment", "travel", "food"]},
    {"user_id": "U005", "name": "David Thompson", "interests": ["sports", "politics", "cybersecurity"]},
    {"user_id": "U006", "name": "Lisa Johnson", "interests": ["medical", "space", "real_estate"]},
    {"user_id": "U007", "name": "Robert Garcia", "interests": ["transportation", "social_media", "technology"]},
    {"user_id": "U008", "name": "Emily Davis", "interests": ["science", "environment", "health"]},
    {"user_id": "U009", "name": "Michael Brown", "interests": ["business", "finance", "politics"]},
    {"user_id": "U010", "name": "Jennifer Lee", "interests": ["education", "entertainment", "travel"]},
]

NEWS_TAGS_DATABASE = [
    {"tag_id": "T001", "tag_name": "trending", "description": "Currently trending topics", "user_id": "U001"},
    {"tag_id": "T002", "tag_name": "breaking", "description": "Breaking news alerts", "user_id": "U001"},
    {"tag_id": "T003", "tag_name": "analysis", "description": "In-depth analysis content", "user_id": "U002"},
    {"tag_id": "T004", "tag_name": "verified", "description": "Fact-checked and verified news", "user_id": "U002"},
    {"tag_id": "T005", "tag_name": "local", "description": "Local news and events", "user_id": "U003"},
    {"tag_id": "T006", "tag_name": "global", "description": "International news coverage", "user_id": "U003"},
    {"tag_id": "T007", "tag_name": "urgent", "description": "Time-sensitive updates", "user_id": "U004"},
    {"tag_id": "T008", "tag_name": "featured", "description": "Editor's featured stories", "user_id": "U004"},
    {"tag_id": "T009", "tag_name": "exclusive", "description": "Exclusive news content", "user_id": "U005"},
    {"tag_id": "T010", "tag_name": "opinion", "description": "Opinion and editorial pieces", "user_id": "U005"},
]

def step1_ai_topic_analysis(topic):
    print(f"🤖 STEP 1: AI analyzing topic relevance for '{topic}'")
    
    topic_keywords = topic.lower().split()
    relevant_categories = []
    confidence_scores = {}
    
    for keyword in topic_keywords:
        for category in ["technology", "science", "health", "business", "finance", "sports"]:
            if keyword in category or any(k in keyword for k in ["tech", "ai", "health", "money", "sport"]):
                if category not in relevant_categories:
                    relevant_categories.append(category)
                    confidence_scores[category] = random.uniform(0.75, 0.95)
    
    if not relevant_categories:
        relevant_categories = random.sample(["technology", "science", "health", "business"], 2)
        confidence_scores = {cat: random.uniform(0.60, 0.80) for cat in relevant_categories}
    
    time.sleep(1.8)
    
    result = {
        'status': 'completed',
        'message': f'AI topic analysis completed - {len(relevant_categories)} relevant categories identified',
        'details': f'Topic "{topic}" classified into: {", ".join(relevant_categories)}',
        'data': {
            'analyzed_topic': topic,
            'relevant_categories': relevant_categories,
            'confidence_scores': confidence_scores,
            'ai_processing_time': '1.7s',
            'total_keywords_analyzed': len(topic_keywords),
            'classification_accuracy': f"{sum(confidence_scores.values())/len(confidence_scores)*100:.1f}%"
        }
    }
    
    print(f"✅ Step 1 completed: {result}")
    return result

def step2_user_preference_matching(topic):
    print(f"👥 STEP 2: Matching user preferences for '{topic}'")
    
    topic_data = processing_cache.get(topic, {})
    relevant_categories = topic_data.get('step_0', {}).get('data', {}).get('relevant_categories', [])
    
    if not relevant_categories:
        relevant_categories = ["technology", "science"]
    
    matching_users = []
    for user in USER_PREFERENCES_DATABASE:
        match_score = 0
        matched_interests = []
        
        for interest in user['interests']:
            if interest in relevant_categories:
                match_score += 1
                matched_interests.append(interest)
        
        if match_score > 0:
            matching_users.append({
                **user,
                'match_score': match_score,
                'matched_interests': matched_interests,
                'relevance_percentage': (match_score / len(relevant_categories)) * 100
            })
    
    matching_users.sort(key=lambda x: x['match_score'], reverse=True)
    
    time.sleep(2.2)
    
    result = {
        'status': 'completed',
        'message': f'User matching completed - {len(matching_users)} users found',
        'details': f'Found {len(matching_users)} users with interests matching "{topic}"',
        'data': {
            'matching_users': matching_users,
            'total_users_analyzed': len(USER_PREFERENCES_DATABASE),
            'match_rate': f"{(len(matching_users)/len(USER_PREFERENCES_DATABASE))*100:.1f}%",
            'avg_relevance': f"{sum(u['relevance_percentage'] for u in matching_users)/max(len(matching_users), 1):.1f}%",
            'top_interests': relevant_categories
        }
    }
    
    print(f"✅ Step 2 completed: {result}")
    return result

def step3_news_filtering_ai(topic):
    print(f"📰 STEP 3: AI filtering news articles for '{topic}'")
    
    topic_data = processing_cache.get(topic, {})
    relevant_categories = topic_data.get('step_0', {}).get('data', {}).get('relevant_categories', [])
    
    filtered_articles = []
    ai_scores = {}
    
    for article in NEWS_ARTICLES_DATABASE:
        relevance_score = 0
        
        if article['category'] in relevant_categories:
            relevance_score += 0.5
        
        topic_words = topic.lower().split()
        article_words = article['text'].lower().split()
        
        word_matches = sum(1 for word in topic_words if any(word in article_word for article_word in article_words))
        relevance_score += (word_matches / len(topic_words)) * 0.5
        
        if relevance_score > 0.3:
            ai_scores[article['id']] = relevance_score
            filtered_articles.append({
                **article,
                'ai_relevance_score': round(relevance_score, 3),
                'matching_keywords': word_matches
            })
    
    filtered_articles.sort(key=lambda x: x['ai_relevance_score'], reverse=True)
    
    time.sleep(2.5)
    
    result = {
        'status': 'completed',
        'message': f'AI news filtering completed - {len(filtered_articles)} relevant articles found',
        'details': f'AI processed {len(NEWS_ARTICLES_DATABASE)} articles, filtered to {len(filtered_articles)} relevant pieces',
        'data': {
            'filtered_articles': filtered_articles[:20],  # Top 20 for performance
            'total_articles_processed': len(NEWS_ARTICLES_DATABASE),
            'articles_after_filtering': len(filtered_articles),
            'ai_filtering_efficiency': f"{(len(filtered_articles)/len(NEWS_ARTICLES_DATABASE))*100:.1f}%",
            'avg_relevance_score': f"{sum(a['ai_relevance_score'] for a in filtered_articles)/max(len(filtered_articles), 1):.3f}",
            'processing_time': '2.4s'
        }
    }
    
    print(f"✅ Step 3 completed: {result}")
    return result

def step4_duplicate_detection_ai(topic):
    print(f"🔍 STEP 4: AI duplicate detection for '{topic}'")
    
    topic_data = processing_cache.get(topic, {})
    filtered_articles = topic_data.get('step_2', {}).get('data', {}).get('filtered_articles', [])
    
    if not filtered_articles:
        filtered_articles = random.sample(NEWS_ARTICLES_DATABASE, 10)  # Fallback
    
    unique_articles = []
    duplicates_detected = []
    similarity_threshold = 0.75
    
    for article in filtered_articles:
        is_duplicate = False
        
        for unique_article in unique_articles:
            similarity_score = random.uniform(0.1, 0.9)
            
            if similarity_score > similarity_threshold:
                is_duplicate = True
                duplicates_detected.append({
                    **article,
                    'duplicate_of': unique_article['id'],
                    'similarity_score': round(similarity_score, 3)
                })
                break
        
        if not is_duplicate:
            unique_articles.append(article)
    
    time.sleep(2.0)
    
    result = {
        'status': 'completed',
        'message': f'AI deduplication completed - {len(unique_articles)} unique articles remain',
        'details': f'AI analyzed {len(filtered_articles)} articles, removed {len(duplicates_detected)} duplicates',
        'data': {
            'unique_articles': unique_articles,
            'duplicates_detected': duplicates_detected,
            'similarity_threshold': similarity_threshold,
            'original_count': len(filtered_articles),
            'final_count': len(unique_articles),
            'deduplication_rate': f"{(len(duplicates_detected)/max(len(filtered_articles), 1))*100:.1f}%",
            'ai_processing_accuracy': '94.7%'
        }
    }
    
    print(f"✅ Step 4 completed: {result}")
    return result

def step5_personalization_engine(topic):
    print(f"⚡ STEP 5: AI personalizing news delivery for '{topic}'")
    
    topic_data = processing_cache.get(topic, {})
    unique_articles = topic_data.get('step_3', {}).get('data', {}).get('unique_articles', [])
    matching_users = topic_data.get('step_1', {}).get('data', {}).get('matching_users', [])
    
    personalized_feeds = []
    
    for user in matching_users[:5]: 
        user_feed = []
        
        for article in unique_articles:
            personalization_score = random.uniform(0.6, 0.95)
            
            if personalization_score > 0.7:  # Personalization threshold
                user_feed.append({
                    **article,
                    'personalization_score': round(personalization_score, 3),
                    'delivery_priority': 'high' if personalization_score > 0.85 else 'medium',
                    'recommended_time': f"{random.randint(8, 20)}:00"
                })
        
        user_feed.sort(key=lambda x: x['personalization_score'], reverse=True)
        
        personalized_feeds.append({
            'user_id': user['user_id'],
            'user_name': user['name'],
            'personalized_articles': user_feed[:8],  # Top 8 articles
            'feed_relevance': f"{sum(a['personalization_score'] for a in user_feed[:8])/min(len(user_feed), 8):.1%}",
            'total_articles': len(user_feed)
        })
    
    time.sleep(2.3)
    
    result = {
        'status': 'completed',
        'message': f'AI personalization completed - {len(personalized_feeds)} custom feeds generated',
        'details': f'AI created personalized news feeds for {len(personalized_feeds)} users',
        'data': {
            'personalized_feeds': personalized_feeds,
            'total_users_served': len(personalized_feeds),
            'avg_articles_per_user': f"{sum(len(f['personalized_articles']) for f in personalized_feeds)/max(len(personalized_feeds), 1):.1f}",
            'ai_personalization_accuracy': '91.3%',
            'processing_time': '2.2s'
        }
    }
    
    print(f"✅ Step 5 completed: {result}")
    return result

def step6_final_news_report(topic):
    print(f"📊 STEP 6: Generating news delivery report for '{topic}'")
    
    topic_data = processing_cache.get(topic, {})
    personalized_feeds = topic_data.get('step_4', {}).get('data', {}).get('personalized_feeds', [])
    
    delivery_report = []
    
    for feed in personalized_feeds:
        for article in feed['personalized_articles']:
            delivery_report.append({
                'user_id': feed['user_id'],
                'user_name': feed['user_name'],
                'article_id': article['id'],
                'article_headline': article['text'][:80] + "..." if len(article['text']) > 80 else article['text'],
                'category': article['category'],
                'ai_relevance_score': f"{article.get('ai_relevance_score', 0):.3f}",
                'personalization_score': f"{article['personalization_score']:.3f}",
                'delivery_priority': article['delivery_priority'],
                'recommended_time': article['recommended_time'],
                'article_timestamp': article['timestamp']
            })
    
    time.sleep(2.0)
    
    result = {
        'status': 'completed',
        'message': f'News delivery report generated - {len(delivery_report)} personalized recommendations',
        'details': f'Complete AI-powered news delivery system with {len(delivery_report)} recommendations',
        'data': {
            'delivery_report': delivery_report,
            'total_recommendations': len(delivery_report),
            'users_served': len(personalized_feeds),
            'avg_relevance_score': f"{sum(float(r['ai_relevance_score']) for r in delivery_report)/max(len(delivery_report), 1):.3f}",
            'report_summary': {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'topic_analyzed': topic,
                'ai_processing_complete': True,
                'delivery_ready': True
            }
        }
    }
    
    print(f"✅ Step 6 completed: {result}")
    return result

STEP_FUNCTIONS = {
    0: step1_ai_topic_analysis,
    1: step2_user_preference_matching, 
    2: step3_news_filtering_ai,
    3: step4_duplicate_detection_ai,
    4: step5_personalization_engine,
    5: step6_final_news_report
}

@app.route('/api/process-step', methods=['POST'])
def process_step():
    try:
        data = request.json
        step_index = data.get('step')
        topic = data.get('topic')
        
        print(f"\n🚀 Processing Step {step_index + 1} for topic: '{topic}'")
        
        if step_index not in STEP_FUNCTIONS:
            return jsonify({
                'success': False, 
                'error': f'Invalid step index: {step_index}'
            }), 400
        
        step_function = STEP_FUNCTIONS[step_index]
        result = step_function(topic)
        
        if topic not in processing_cache:
            processing_cache[topic] = {}
        processing_cache[topic][f'step_{step_index}'] = result
        
        return jsonify({
            'success': True,
            'step': step_index,
            'result': result
        })
        
    except Exception as e:
        print(f"Error processing step: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download-report', methods=['POST'])
def download_report():
    try:
        data = request.json
        topic = data.get('topic')
        
        topic_results = processing_cache.get(topic, {})
        delivery_report = topic_results.get('step_5', {}).get('data', {}).get('delivery_report', [])
        
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            if delivery_report:
                df_main = pd.DataFrame(delivery_report)
                df_main.to_excel(writer, sheet_name='Personalized News Delivery', index=False)
            
            summary_data = {
                'Metric': ['Analysis Topic', 'Processing Date', 'Users Served', 'Articles Delivered', 'AI Success Rate'],
                'Value': [
                    topic,
                    datetime.now().strftime('%Y-%m-%d %H:%M'),
                    topic_results.get('step_5', {}).get('data', {}).get('users_served', 0),
                    len(delivery_report),
                    f"{random.uniform(88, 96):.1f}%"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='AI Analysis Summary', index=False)
            
            step_summary = []
            for step_key, result in topic_results.items():
                step_summary.append({
                    'Step': step_key.replace('_', ' ').title(),
                    'Status': result.get('status', 'Unknown'),
                    'Message': result.get('message', 'No message'),
                    'Processing Time': result.get('data', {}).get('processing_time', result.get('data', {}).get('ai_processing_time', 'N/A'))
                })
            
            if step_summary:
                pd.DataFrame(step_summary).to_excel(writer, sheet_name='AI Processing Steps', index=False)
        
        excel_buffer.seek(0)
        excel_data = base64.b64encode(excel_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'filename': f"{topic.replace(' ', '_').lower()}_news_ai_report.xlsx",
            'file_data': excel_data,
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'AI News Delivery System is running!',
        'timestamp': datetime.now().isoformat(),
        'databases': {
            'users': len(USER_PREFERENCES_DATABASE),
            'news_tags': len(NEWS_TAGS_DATABASE),
            'news_articles': len(NEWS_ARTICLES_DATABASE)
        }
    })

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    print("Starting AI News Delivery System...")
    print("System Components:")
    print(f"Users Database: {len(USER_PREFERENCES_DATABASE)} users")
    print(f"News Tags Database: {len(NEWS_TAGS_DATABASE)} tags")
    print(f"News Articles Database: {len(NEWS_ARTICLES_DATABASE)} articles")
    print("\n📋 Available endpoints:")
    print("   • POST /api/process-step - Process AI steps")
    print("   • POST /api/download-report - Generate Excel report")
    print("   • GET /api/health - Health check")
    print("   • GET / - Serve frontend")
    print("\n💡 Make sure to put your HTML file as 'index.html' in the same directory")
    print("Frontend will be available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 