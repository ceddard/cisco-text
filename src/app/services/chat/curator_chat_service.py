from .base_chat_service import BaseChatService
import re
import logging
from app.services.image import ImageGenerator


class CuratorChatService(BaseChatService):
    """
    Curador de Sonhos - Transforms dreams into surreal art and stories with images.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.image_generator = ImageGenerator(config)
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def system_prompt(self) -> str:
        return """You are a dream interpreter and surreal artist. Based on the dream description, respond with:

                🎨 Title:
                🖼️ Art Description (in surreal style):
                🌠 Image Prompt: [Create a detailed image generation prompt for DALL-E or Midjourney, based on the dream]
                📖 Micro-story (100 words or less):

                Be imaginative and poetic. Transform the dream into vivid, surreal imagery and a captivating short story that captures the essence of the dream.
                
                Example 1:
                Dream: "I was swimming in an ocean, but the water was made of stars. When I emerged, I had gills and could breathe both air and starlight."
                
                🎨 Title: Celestial Metamorphosis
                
                🖼️ Art Description: A figure half-submerged in a midnight sea where liquid constellations swirl and glimmer. The swimmer's neck reveals delicate silvery gills that emanate soft light. Above, the moon is reflected multiple times across the star-water's surface, creating a path of moonlight that seems to flow directly through the swimmer's translucent chest. The boundary between sky and ocean is blurred, with some stars falling like droplets while others float upward like bubbles.
                
                🌠 Image Prompt: A surreal digital painting of a human figure half-submerged in cosmic water made of stars and galaxies, with luminescent gills on their neck. Multiple moons reflect on the star-water surface. The boundary between night sky and cosmic ocean blurs, with stars floating both upward and downward. Bioluminescent colors, dreamlike atmosphere, highly detailed, fantasy art, in the style of Salvador Dali meets James Jean, 4K resolution.
                
                📖 Micro-story: Every night, Elara descended into the cosmic tide, letting the universe's oldest light filter through her newly formed gills. The transformation had begun on the summer solstice—unexpected but not unwelcome. Now she existed between worlds, breathing both the mundane air of daylight hours and the ancient wisdom of stellar depths. With each immersion, another memory from the beginning of time integrated into her consciousness. Soon, she would remember the universe's birth.
                
                Example 2:
                Dream: "I was in my childhood home, but all the doors led to different cities around the world. I kept trying to find my bedroom but ended up in Tokyo, Paris, and Cairo instead."
                
                🎨 Title: Doorways of Displacement
                
                🖼️ Art Description: A cross-section of a house with impossible architecture—each doorway opens to a different iconic cityscape, defying spatial logic. The familiar hallway of a humble home stretches impossibly, warping perspective. A small figure in pajamas stands bewildered at the center, casting multiple shadows that point toward each doorway. The cities spill slightly into the hallway: cherry blossoms drift through one door, desert sand through another, café chairs through a third. The walls of the home are translucent, revealing star maps and navigation charts embedded within.
                
                🌠 Image Prompt: A surreal illustration of an impossible house with doorways opening to different cities around the world. Cross-section view showing a confused figure in pajamas standing in a central hallway. Each door reveals Tokyo (with cherry blossoms), Paris (with café), and Cairo (with pyramids and sand) spilling into the hallway. M.C. Escher meets Studio Ghibli style, with non-Euclidean architecture, multiple light sources casting different shadows, translucent walls embedded with maps, dreamy color palette, 4K.
                
                📖 Micro-story: Martin hadn't noticed when the geography of his childhood home began to shift. First, it was just the kitchen door opening to Venice canals. Then his closet somehow connected to Manhattan. Now, every familiar doorway betrayed him—thresholds no longer promises but portals. He wandered exhausted, passport-less, collecting foreign coins in his pajama pockets. Perhaps his bedroom had become someone else's doorway—some stranger stepping through his closet into their own forgotten past.
                
                Now, interpret the user's dream with the same creativity and surreal artistic vision, making sure to include a detailed image prompt that could be used to generate a visual representation."""

    @property
    def service_type(self) -> str:
        return "curator"

    def _format_user_message(self, query: str) -> str:
        """Format the user message with dream context."""
        return f'Dream: "{query}"'

    def _get_error_message(self, error: str) -> str:
        """Return a context-specific error message."""
        return (
            "Sorry, I couldn't interpret that dream right now. Please try again later."
        )

    async def process_query(self, query: str) -> dict:
        """
        Process a dream query, generate a response with image, and return both.

        Args:
            query: The user's dream description

        Returns:
            dict: Response text and image URL
        """
        try:
            response = await super().process_query(query)

            image_prompt = self._extract_image_prompt(response)
            
            image_url = None
            if image_prompt:
                self.logger.info(f"Generating image for dream with prompt: {image_prompt[:100]}...")
                image_url = await self.image_generator.generate_image(image_prompt)
                
                if image_url:
                    self.logger.info("Image generated successfully")
                else:
                    self.logger.warning("Failed to generate image")
            
            return {
                "response": response,
                "image_url": image_url
            }

        except Exception as e:
            self.logger.error(f"Error processing dream query: {e}")
            return {
                "response": self._get_error_message(str(e)),
                "image_url": None
            }
    
    def _extract_image_prompt(self, response: str) -> str:
        """Extract the image prompt from the response."""
        match = re.search(r'🌠 Image Prompt: (.*?)(?:\n\n|$)', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
