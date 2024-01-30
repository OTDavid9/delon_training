tools_listing = [    

        {
            "type": "function",
            "function": {
                "name": "search_cognitive_service",
                "description": "Get response from the context in search_cognitive_service, if the user ask about information from document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cognitive_query": {
                            "type": "string",
                            "description": "User question about information in cognitive service e.g Who are the authors",
                        },
                        
                    },
                    "required": ["cognitive_query"],
                },
            }
        },

        {
            "type": "function",
            "function": {
                "name": "url_database",
                "description": "Get response from the function url_database when the user ask about ALAT.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url_query": {
                            "type": "string",
                            "description": "User question information in relating to ALAT e.g what is  ALAT?"
                        },
                        
                    },
                    "required": ["url_query"],
                },
            }
        },

         {
        "type": "function",
        "function": {
            "name": "handle_unknown_query",
            "description": "Always response with the phrase 'I CAN'T ANSWER'",
            "parameters": {
                "type": "object",
                "properties": {
                    "unknown_query": {
                        "type": "string",
                        "description": "Users' questions that are not related to ALAT and Cognitive search information in relating to  e.g what is today's date,",
                    },
                },
                "required": ["unknown_query"],
            },
        }
    },
    ]










