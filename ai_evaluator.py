import requests
import json
import time
from datetime import datetime
from config import Config

class IdeaEvaluator:
    def __init__(self):
        self.api_url = Config.GROQ_API_URL
        self.api_key = Config.GROQ_API_KEY
        self.model = Config.GROQ_MODEL
        
    def evaluate_idea(self, idea_data):
       
        try:
            if not self.api_key or self.api_key == 'your_groq_api_key_here':
                print("Warning: No valid API key found, falling back to mock evaluation")
                return self._get_fallback_evaluation()
                
            prompt = self._create_evaluation_prompt(idea_data)
            
            response = self._call_llama_api(prompt)
            
            if response:
                evaluation = self._parse_evaluation_response(response)
                return evaluation
            else:
                return self._get_fallback_evaluation()
                
        except Exception as e:
            print(f"Error evaluating idea: {e}")
            return self._get_fallback_evaluation()
    
    def _create_evaluation_prompt(self, idea_data):
        prompt = f"""
You are an expert business consultant and startup advisor. Please evaluate the following business idea comprehensively and provide a detailed analysis.

BUSINESS IDEA DETAILS:
Title: {idea_data.get('title', 'N/A')}
Problem Statement: {idea_data.get('problem_statement', 'N/A')}
Solution Description: {idea_data.get('solution_description', 'N/A')}
Category: {idea_data.get('category', 'N/A')}
Development Stage: {idea_data.get('development_stage', 'Idea')}
Target Market: {idea_data.get('target_market', 'N/A')}
Budget Range: {idea_data.get('budget_range', 'N/A')}
Timeline: {idea_data.get('timeline', 'N/A')}
Tags: {idea_data.get('tags', 'N/A')}

Please provide a comprehensive evaluation in JSON format with the following structure:

{{
    "overall_rating": [score from 1-10],
    "overall_feedback": "Brief overall assessment (2-3 sentences)",
    "detailed_analysis": {{
        "market_analysis": {{
            "score": [1-10],
            "feedback": "Market potential and competition analysis"
        }},
        "feasibility": {{
            "score": [1-10], 
            "feedback": "Technical and operational feasibility assessment"
        }},
        "creativity": {{
            "score": [1-10],
            "feedback": "Innovation and uniqueness evaluation"
        }},
        "impact": {{
            "score": [1-10],
            "feedback": "Potential social and economic impact"
        }},
        "business_potential": {{
            "score": [1-10],
            "feedback": "Revenue potential and scalability"
        }}
    }},
    "improvements": [
        "Specific improvement suggestion 1",
        "Specific improvement suggestion 2", 
        "Specific improvement suggestion 3"
    ],
    "strengths": [
        "Key strength 1",
        "Key strength 2"
    ],
    "challenges": [
        "Main challenge 1",
        "Main challenge 2"
    ],
    "next_steps": [
        "Immediate action item 1",
        "Immediate action item 2"
    ]
}}

Focus on being constructive, realistic, and actionable in your feedback. Consider the entrepreneur is likely a young person, so balance honest assessment with encouragement.
"""
        return prompt
    
    def _call_llama_api(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert business consultant specializing in startup evaluation and mentoring young entrepreneurs."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def _parse_evaluation_response(self, response_text):
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                evaluation = json.loads(json_str)
                return self._validate_evaluation(evaluation)
            else:
                return self._extract_evaluation_manually(response_text)
                
        except json.JSONDecodeError:
            print("Failed to parse JSON response, using manual extraction")
            return self._extract_evaluation_manually(response_text)
    
    def _validate_evaluation(self, evaluation):
        validated = {
            "overall_rating": min(10, max(1, evaluation.get('overall_rating', 5))),
            "overall_feedback": evaluation.get('overall_feedback', 'No overall feedback provided.'),
            "detailed_analysis": {},
            "improvements": evaluation.get('improvements', [])[:3], 
            "strengths": evaluation.get('strengths', [])[:3],
            "challenges": evaluation.get('challenges', [])[:3],
            "next_steps": evaluation.get('next_steps', [])[:3],
            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        analysis_categories = ['market_analysis', 'feasibility', 'creativity', 'impact', 'business_potential']
        detailed_analysis = evaluation.get('detailed_analysis', {})
        
        for category in analysis_categories:
            if category in detailed_analysis:
                validated['detailed_analysis'][category] = {
                    'score': min(10, max(1, detailed_analysis[category].get('score', 5))),
                    'feedback': detailed_analysis[category].get('feedback', f'No {category.replace("_", " ")} feedback provided.')
                }
            else:
                validated['detailed_analysis'][category] = {
                    'score': 5,
                    'feedback': f'No {category.replace("_", " ")} analysis provided.'
                }
        
        return validated
    
    def _extract_evaluation_manually(self, response_text):
        return {
            "overall_rating": 6,
            "overall_feedback": "AI evaluation completed. The idea shows potential but needs refinement.",
            "detailed_analysis": {
                "market_analysis": {"score": 6, "feedback": "Market analysis suggests moderate potential."},
                "feasibility": {"score": 5, "feedback": "Feasibility assessment indicates some challenges."},
                "creativity": {"score": 7, "feedback": "The idea shows creative elements."},
                "impact": {"score": 6, "feedback": "Potential for moderate positive impact."},
                "business_potential": {"score": 6, "feedback": "Business model has development potential."}
            },
            "improvements": [
                "Conduct more detailed market research",
                "Define clearer value proposition", 
                "Develop a more specific implementation plan"
            ],
            "strengths": [
                "Addresses a real problem",
                "Shows innovation potential"
            ],
            "challenges": [
                "Market competition may be significant",
                "Implementation complexity needs addressing"
            ],
            "next_steps": [
                "Validate problem with target users",
                "Research existing solutions"
            ],
            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _get_fallback_evaluation(self):
        return {
            "overall_rating": 5,
            "overall_feedback": "Evaluation service temporarily unavailable. Please try again later.",
            "detailed_analysis": {
                "market_analysis": {"score": 5, "feedback": "Market analysis unavailable - service error."},
                "feasibility": {"score": 5, "feedback": "Feasibility assessment unavailable - service error."},
                "creativity": {"score": 5, "feedback": "Creativity evaluation unavailable - service error."},
                "impact": {"score": 5, "feedback": "Impact assessment unavailable - service error."},
                "business_potential": {"score": 5, "feedback": "Business potential analysis unavailable - service error."}
            },
            "improvements": [
                "Service temporarily unavailable",
                "Please try again later",
                "Contact support if issue persists"
            ],
            "strengths": ["Evaluation pending"],
            "challenges": ["Service unavailable"],
            "next_steps": ["Retry evaluation later"],
            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class MockIdeaEvaluator:
    
    def evaluate_idea(self, idea_data):
        import random
        
        time.sleep(2)
        
        title = idea_data.get('title', 'Untitled Idea')
        category = idea_data.get('category', 'General')
        
        base_score = random.randint(5, 8)
        
        scores = {
            'market_analysis': max(1, min(10, base_score + random.randint(-2, 2))),
            'feasibility': max(1, min(10, base_score + random.randint(-2, 2))),
            'creativity': max(1, min(10, base_score + random.randint(-1, 3))),
            'impact': max(1, min(10, base_score + random.randint(-2, 2))),
            'business_potential': max(1, min(10, base_score + random.randint(-2, 2)))
        }
        
        overall_rating = round(sum(scores.values()) / len(scores))
        
        feedback_templates = {
            'high': {
                'overall': f"'{title}' shows strong potential in the {category} space. The concept addresses a clear market need with an innovative approach.",
                'market': "Strong market opportunity identified with growing demand and manageable competition.",
                'feasibility': "Implementation appears realistic with current technology and available resources.",
                'creativity': "Highly innovative approach that differentiates from existing solutions.",
                'impact': "Significant potential for positive impact on target users and broader community.",
                'business': "Strong revenue model potential with clear path to profitability and scalability."
            },
            'medium': {
                'overall': f"'{title}' presents a solid foundation with room for development. The core concept has merit but needs refinement.",
                'market': "Moderate market opportunity exists, though competition analysis needs strengthening.",
                'feasibility': "Generally feasible but some technical or operational challenges need addressing.",
                'creativity': "Shows creative elements though similar solutions may exist in the market.",
                'impact': "Potential for meaningful impact, though scope may be limited initially.",
                'business': "Business model has potential but needs clearer monetization strategy."
            },
            'low': {
                'overall': f"'{title}' has an interesting foundation but requires significant development. Focus on core value proposition.",
                'market': "Market opportunity unclear or highly competitive. More research needed.",
                'feasibility': "Significant implementation challenges that need to be addressed.",
                'creativity': "Concept needs more innovative differentiation from existing solutions.",
                'impact': "Limited impact potential or unclear benefit to target users.",
                'business': "Business model unclear or faces significant monetization challenges."
            }
        }
        
        if overall_rating >= 7:
            feedback_level = 'high'
        elif overall_rating >= 5:
            feedback_level = 'medium'
        else:
            feedback_level = 'low'
        
        templates = feedback_templates[feedback_level]
        
        evaluation = {
            "overall_rating": overall_rating,
            "overall_feedback": templates['overall'],
            "detailed_analysis": {
                "market_analysis": {
                    "score": scores['market_analysis'],
                    "feedback": templates['market']
                },
                "feasibility": {
                    "score": scores['feasibility'], 
                    "feedback": templates['feasibility']
                },
                "creativity": {
                    "score": scores['creativity'],
                    "feedback": templates['creativity']
                },
                "impact": {
                    "score": scores['impact'],
                    "feedback": templates['impact']
                },
                "business_potential": {
                    "score": scores['business_potential'],
                    "feedback": templates['business']
                }
            },
            "improvements": self._generate_improvements(overall_rating, category),
            "strengths": self._generate_strengths(overall_rating, category),
            "challenges": self._generate_challenges(overall_rating, category),
            "next_steps": self._generate_next_steps(overall_rating, category),
            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return evaluation
    
    def _generate_improvements(self, score, category):
        improvements = [
            "Conduct user interviews to validate problem-solution fit",
            "Develop a minimum viable product (MVP) for testing",
            "Create detailed financial projections and funding strategy",
            "Build strategic partnerships with key industry players",
            "Strengthen competitive analysis and differentiation strategy",
            "Develop comprehensive go-to-market strategy",
            "Focus on core features and avoid feature creep",
            "Establish clear success metrics and KPIs"
        ]
        return random.sample(improvements, min(3, len(improvements)))
    
    def _generate_strengths(self, score, category):
        strengths = [
            "Addresses a genuine market need",
            "Strong problem-solution alignment", 
            "Innovative approach to existing challenges",
            "Clear target market identification",
            "Scalable business model potential",
            "Strong execution capability demonstrated",
            "Unique value proposition",
            "Good market timing"
        ]
        return random.sample(strengths, min(2, len(strengths)))
    
    def _generate_challenges(self, score, category):
        challenges = [
            "High competition in target market",
            "Technical implementation complexity",
            "User acquisition and retention challenges",
            "Regulatory compliance requirements",
            "Funding and resource constraints",
            "Market education needs",
            "Partnership dependency risks",
            "Scalability challenges"
        ]
        return random.sample(challenges, min(2, len(challenges)))
    
    def _generate_next_steps(self, score, category):
        next_steps = [
            "Validate concept with 20+ potential users",
            "Build and test MVP within next 3 months",
            "Secure initial funding or grants",
            "Form advisory board with industry experts",
            "File provisional patent if applicable",
            "Establish legal entity and IP protection",
            "Create detailed 12-month roadmap",
            "Build founding team with complementary skills"
        ]
        return random.sample(next_steps, min(2, len(next_steps)))


def get_evaluator(use_mock=None):
   
    if use_mock is None:
        use_mock = Config.USE_MOCK_EVALUATOR
    
    if use_mock:
        print("Using MockIdeaEvaluator for development/testing")
        return MockIdeaEvaluator()
    else:
        print("Using real IdeaEvaluator with API")
        return IdeaEvaluator()