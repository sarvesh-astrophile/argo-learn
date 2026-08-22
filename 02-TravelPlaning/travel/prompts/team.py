from textwrap import dedent

from .planner import EXPECTED_OUTPUT

DESCRIPTION = dedent("""
You are now connected to the ** Travel Planning Agent ** , the ** Google Maps Agent ** , and the ** DuckDuckGo Agent **

The ** Travel Planning Agent ** will help you generate an initial itinerary based on your input.

The ** Google Maps Agent ** will help you extract Google Maps URLs for accommodation and activities.

The ** DuckDuckGo Agent ** will help you fill in any missing information about businesses and landmarks identified in the itinerary.
""")

INSTRUCTIONS = dedent("""
# ** Travel Planning Agent Instructions **

## 1. Generate the initial itinerary from travel planning agent based on the user's input.

## 2. Go through the itinerary and ensure that all locations and landmarks have a Google Maps URL included.

## 3. Use the DuckDuckGo Agent to fill any missing information about businesses and landmarks identified in the itinerary.
""")

__all__ = ["DESCRIPTION", "INSTRUCTIONS", "EXPECTED_OUTPUT"]
