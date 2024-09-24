import json
import streamlit as st
from groq import AsyncGroq
from utils import GROQ_API_KEY, LLM_MODEL, format_web_results, FACT_CHECKING_ERROR, JSON_PARSING_ERROR, UNEXPECTED_ERROR

async def fact_check_with_groq(groq_client, statement, context, web_results, categories, sentiment, status_queue):
    web_info = format_web_results(web_results)

    prompt = f"""
    ## Fact-Checking Request

    **Context Summary:** {context}

    **Statement to Verify:** {statement}

    **Web Search Results:**
    {web_info}

    **Categories:** {', '.join(categories)}

    **Sentiment Score:** {sentiment}

    ## Instructions:

    1. Verify the statement based on the context and the web search results.
    2. Assess the credibility of the sources in the web search results.
    3. Look for signs of bias in the statement and the sources.
    4. Consider the categories and sentiment score in your analysis.

    ## Response Format:

    ```json
    {{
      "Verification": "[VERIFIED, PARTIALLY VERIFIED, NOT VERIFIED]",
      "Confidence": "[HIGH, MEDIUM, LOW]",
      "Explanation": "[Your concise explanation]",
      "Bias": "[Any detected bias or 'None detected']",
      "Sources": "[List of relevant sources with URLs]",
      "Categories": "{categories}",
      "Sentiment": {sentiment}
    }}
    ```
    """
    print(f"Prompt sent to GROQ API:\n{prompt}")

    try:
        response = await groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly knowledgeable AI assistant specializing in quick, real-time fact-checking for debates, with access to recent web information and debate context.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=LLM_MODEL,  
            temperature=0.1,
            max_tokens=300,
            top_p=1,
        )
        print(f"Response received from GROQ API:\n{response.choices[0].message.content}")
        return response.choices[0].message.content

    except Exception as e:
        st.error(FACT_CHECKING_ERROR.format(str(e)))
        return json.dumps({
            "Verification": "ERROR",
            "Confidence": "N/A",
            "Explanation": FACT_CHECKING_ERROR.format(str(e)),
            "Bias": "N/A",
            "Sources": "N/A",
            "Categories": "N/A",
            "Sentiment": "N/A"
        })

def parse_fact_check_result(result_string):
    try:
        # Remove any leading/trailing whitespace and backticks
        result_string = result_string.strip().strip('`')
        
        # If the string starts with "json", remove it
        if result_string.startswith('json'):
            result_string = result_string[4:].strip()
        
        # Parse the JSON string
        result = json.loads(result_string)
        
        # Ensure all required fields are present
        required_fields = ["Verification", "Confidence", "Explanation", "Bias", "Sources", "Categories", "Sentiment"]
        for field in required_fields:
            if field not in result:
                result[field] = "N/A"
        
        return result
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Problematic JSON string: {result_string}")
        # Attempt to extract partial information
        partial_result = {}
        for field in ["Verification", "Confidence", "Explanation", "Bias", "Sources", "Categories", "Sentiment"]:
            field_start = result_string.find(f'"{field}":')
            if field_start != -1:
                field_end = result_string.find(',', field_start)
                if field_end == -1:
                    field_end = result_string.find('}', field_start)
                if field_end != -1:
                    partial_result[field] = result_string[field_start:field_end].split(':')[1].strip().strip('"')
        
        if partial_result:
            print(f"Extracted partial result: {partial_result}")
            return partial_result
        else:
            return {
                "Verification": "ERROR",
                "Confidence": "N/A",
                "Explanation": JSON_PARSING_ERROR.format(str(e)),
                "Bias": "N/A",
                "Sources": "N/A",
                "Categories": "N/A",
                "Sentiment": "N/A"
            }
    except Exception as e:
        print(UNEXPECTED_ERROR.format(str(e)))
        return {
            "Verification": "ERROR",
            "Confidence": "N/A",
            "Explanation": UNEXPECTED_ERROR.format(str(e)),
            "Bias": "N/A",
            "Sources": "N/A",
            "Categories": "N/A",
            "Sentiment": "N/A"
        }