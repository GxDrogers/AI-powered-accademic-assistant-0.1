import re
import json
import random
import os
import sys
sys.path.append('..')
import config

class QueryProcessor:
    def __init__(self):
        # Load academic knowledge base
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        # This would typically load from a JSON file or database
        # For this example, we'll create a simple in-memory knowledge base
        
        return {
            "math": {
                "algebra": {
                    "quadratic formula": "The quadratic formula is x = (-b ± √(b² - 4ac)) / 2a",
                    "factoring": "Factoring is the process of finding expressions that multiply to give a polynomial",
                    "linear equation": "A linear equation is an equation where the highest power of the variable is 1"
                },
                "calculus": {
                    "derivative": "The derivative measures the rate of change of a function with respect to a variable",
                    "integral": "Integration is the process of finding a function from its derivative",
                    "limit": "A limit is the value a function approaches as the input approaches some value"
                }
            },
            "science": {
                "physics": {
                    "newton's laws": "Newton's three laws describe the relationship between motion and force",
                    "gravity": "Gravity is the force that attracts two bodies with mass towards each other",
                    "energy": "Energy is the capacity to do work and comes in various forms like kinetic and potential"
                },
                "chemistry": {
                    "periodic table": "The periodic table organizes elements by atomic number and chemical properties",
                    "chemical reaction": "A chemical reaction is a process that transforms one set of chemicals into another",
                    "atomic structure": "Atoms consist of a nucleus containing protons and neutrons, surrounded by electrons"
                }
            },
            "language": {
                "grammar": {
                    "verb": "A verb is a word that describes an action, state, or occurrence",
                    "noun": "A noun is a word that identifies people, places, things, or ideas",
                    "adjective": "An adjective is a word that describes a noun or pronoun"
                },
                "literature": {
                    "shakespeare": "William Shakespeare was an English playwright and poet, widely regarded as the greatest writer in the English language",
                    "novel": "A novel is a long narrative that describes fictional characters and events",
                    "poetry": "Poetry is a form of literature that uses aesthetic and rhythmic qualities of language"
                }
            }
        }
    
    def process_query(self, query):
        # Convert to lowercase for easier matching
        query = query.lower()
        
        # Extract key terms
        key_terms = self._extract_key_terms(query)
        
        # Search the knowledge base
        response = self._search_knowledge_base(key_terms, query)
        
        # If no specific answer is found, provide a general response
        if not response:
            general_responses = [
                "I'm not sure about that specific topic. Could you ask a more general question?",
                "I don't have information on that specific question. Can I help with something else?",
                "That's a bit outside my current knowledge base. Let's discuss something I can assist with.",
                "I'm still learning about that topic. Could you ask about something else?"
            ]
            response = random.choice(general_responses)
        
        return response
    
    def _extract_key_terms(self, query):
        # Remove common words and keep important ones
        common_words = [
            "what", "is", "the", "a", "an", "of", "in", "for", "to", "and",
            "or", "can", "you", "tell", "me", "about", "explain", "define"
        ]
        
        words = query.split()
        key_terms = [word for word in words if word not in common_words]
        
        return key_terms
    
    def _search_knowledge_base(self, key_terms, full_query):
        # First, try direct matches in the knowledge base
        for category in self.knowledge_base:
            for subcategory in self.knowledge_base[category]:
                for topic, info in self.knowledge_base[category][subcategory].items():
                    # Check if topic matches any key terms
                    if any(term in topic for term in key_terms):
                        return info
        
        # If no direct match, try more flexible matching
        for category in self.knowledge_base:
            for subcategory in self.knowledge_base[category]:
                # Check if category or subcategory matches
                if category in full_query or subcategory in full_query:
                    # Return a relevant piece of information
                    topics = list(self.knowledge_base[category][subcategory].keys())
                    if topics:
                        topic = topics[0]  # Just pick the first one
                        return f"On {topic}: {self.knowledge_base[category][subcategory][topic]}"
        
        return None