from typing import Any, Dict, List
import logging
import os
from datetime import datetime

# Image processing imports (optional)
try:
    import cv2
    import numpy as np
    from PIL import Image
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    logging.warning("Image processing libraries not available. Image analysis features will be limited.")

class ImageAnalysisManager:
    """Manages the image analysis process of the research agent."""

    def __init__(self, agent):
        self.agent = agent

    def analyze_images(self, image_paths: List[str]) -> Dict[str, Any]:
        """Analyze uploaded images for content recognition."""
        if not IMAGE_PROCESSING_AVAILABLE:
            return {"error": "Image processing libraries not available"}

        results = {
            "image_analysis": [],
            "total_images": len(image_paths),
            "analysis_timestamp": datetime.now().isoformat()
        }

        for image_path in image_paths:
            try:
                image_result = self._analyze_single_image(image_path)
                results["image_analysis"].append(image_result)
            except Exception as e:
                logging.error(f"Failed to analyze image {image_path}: {e}")
                results["image_analysis"].append({
                    "path": image_path,
                    "error": str(e)
                })

        return results

    def _analyze_single_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze a single image for content and features."""
        if not os.path.exists(image_path):
            return {"path": image_path, "error": "File not found"}

        try:
            # Load image with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return {"path": image_path, "error": "Could not load image"}

            # Basic image properties
            height, width, channels = image.shape
            file_size = os.path.getsize(image_path)

            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Calculate basic statistics
            mean_brightness = np.mean(gray)
            std_brightness = np.std(gray)

            # Edge detection (simple feature extraction)
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.count_nonzero(edges) / (height * width)

            # Color analysis
            color_analysis = self._analyze_image_colors(image)

            # Content classification (simple rule-based approach)
            content_classification = self._classify_image_content(image, gray, color_analysis)

            return {
                "path": image_path,
                "filename": os.path.basename(image_path),
                "dimensions": f"{width}x{height}",
                "file_size": file_size,
                "channels": channels,
                "mean_brightness": float(mean_brightness),
                "brightness_variation": float(std_brightness),
                "edge_density": float(edge_density),
                "color_analysis": color_analysis,
                "dominant_colors": color_analysis.get("dominant_colors", []),
                "content_classification": content_classification,
                "primary_category": content_classification.get("primary_category", "unknown"),
                "confidence": content_classification.get("confidence", 0.0),
                "analysis_success": True
            }

        except Exception as e:
            return {"path": image_path, "error": str(e)}

    def _analyze_image_colors(self, image) -> Dict[str, Any]:
        """Analyze color distribution in image."""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

            # Calculate color histograms
            hist_b = cv2.calcHist([image], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([image], [2], None, [256], [0, 256])

            # Find dominant colors (simplified)
            dominant_colors = []
            for i, (hist, color) in enumerate([(hist_b, "Blue"), (hist_g, "Green"), (hist_r, "Red")])):
                peak_idx = np.argmax(hist)
                dominant_colors.append({
                    "color": color,
                    "peak_intensity": int(peak_idx),
                    "strength": float(hist[peak_idx])
                })

            return {
                "dominant_colors": dominant_colors,
                "color_space_analysis": {
                    "hsv_available": True,
                    "lab_available": True
                }
            }

        except Exception as e:
            return {"error": str(e)}

    def _classify_image_content(self, image, gray, color_analysis) -> Dict[str, Any]:
        """Classify image content using simple rule-based approach."""
        try:
            height, width = gray.shape
            aspect_ratio = width / height

            # Get color information
            dominant_colors = color_analysis.get("dominant_colors", [])

            # Calculate various features
            mean_brightness = np.mean(gray)
            std_brightness = np.std(gray)

            # Edge density for texture analysis
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.count_nonzero(edges) / (height * width)

            # Color saturation analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            saturation_mean = np.mean(hsv[:, :, 1])

            # Initialize classification scores
            categories = {
                "animals": 0.0,
                "nature": 0.0,
                "technology": 0.0,
                "food": 0.0,
                "architecture": 0.0,
                "people": 0.0,
                "transportation": 0.0
            }

            # Rule-based classification logic

            # Animals: Often have organic shapes, moderate saturation, varied textures
            if 0.3 < saturation_mean < 0.7 and 0.1 < edge_density < 0.3:
                categories["animals"] += 0.4
            if aspect_ratio > 1.2:  # Landscape orientation common for animal photos
                categories["animals"] += 0.2

            # Nature: High saturation, natural colors (greens, blues), organic textures
            green_dominance = any(c["color"] == "Green" and c["peak_intensity"] > 100 for c in dominant_colors)
            blue_dominance = any(c["color"] == "Blue" and c["peak_intensity"] > 120 for c in dominant_colors)
            if green_dominance or blue_dominance:
                categories["nature"] += 0.5
            if saturation_mean > 0.6:
                categories["nature"] += 0.3

            # Technology: Sharp edges, high contrast, geometric shapes, cool colors
            if edge_density > 0.2 and std_brightness > 50:
                categories["technology"] += 0.4
            if aspect_ratio < 0.8:  # Portrait orientation common for devices
                categories["technology"] += 0.2

            # Food: Warm colors, moderate saturation, varied textures
            red_dominance = any(c["color"] == "Red" and c["peak_intensity"] > 80 for c in dominant_colors)
            if red_dominance and 0.4 < saturation_mean < 0.8:
                categories["food"] += 0.5

            # Architecture: Strong lines, geometric shapes, urban colors
            if edge_density > 0.15 and std_brightness > 40:
                categories["architecture"] += 0.3
            if mean_brightness > 150:  # Often bright/white buildings
                categories["architecture"] += 0.2

            # People: Skin tones, portrait aspect ratios, moderate contrast
            # Look for flesh tones in HSV space
            skin_pixels = np.count_nonzero(
                (hsv[:, :, 0] >= 5) & (hsv[:, :, 0] <= 25) &  # Hue range for skin
                (hsv[:, :, 1] >= 20) & (hsv[:, :, 2] >= 50)   # Saturation and value
            )
            skin_ratio = skin_pixels / (height * width)
            if skin_ratio > 0.05:  # At least 5% skin pixels
                categories["people"] += 0.6
            if 0.5 < aspect_ratio < 0.8:  # Portrait orientation
                categories["people"] += 0.2

            # Transportation: Metallic colors, geometric shapes, motion blur detection
            metallic_colors = any(
                (c["color"] == "Blue" and 150 < c["peak_intensity"] < 200) or
                (c["color"] == "Red" and 100 < c["peak_intensity"] < 150)
                for c in dominant_colors
            )
            if metallic_colors and edge_density > 0.12:
                categories["transportation"] += 0.4

            # Find the category with highest score
            primary_category = max(categories.keys(), key=lambda k: categories[k])
            confidence = categories[primary_category]

            # If confidence is too low, classify as unknown
            if confidence < 0.2:
                primary_category = "unknown"
                confidence = 0.0

            return {
                "categories": categories,
                "primary_category": primary_category,
                "confidence": confidence,
                "features": {
                    "aspect_ratio": aspect_ratio,
                    "mean_brightness": mean_brightness,
                    "edge_density": edge_density,
                    "saturation_mean": saturation_mean,
                    "skin_ratio": skin_ratio if 'skin_ratio' in locals() else 0.0
                }
            }

        except Exception as e:
            return {
                "error": str(e),
                "primary_category": "unknown",
                "confidence": 0.0
            }

    def search_similar_images(self, image_paths: List[str], max_results: int = 10) -> Dict[str, Any]:
        """Search for similar images on the web."""
        results = {
            "search_results": [],
            "total_searched": len(image_paths),
            "max_results_per_image": max_results,
            "search_timestamp": datetime.now().isoformat()
        }

        for image_path in image_paths:
            try:
                # First analyze the uploaded image to determine its content
                image_analysis = self._analyze_single_image(image_path)
                detected_category = image_analysis.get("primary_category", "unknown")

                similar_images = self._search_similar_images_web(image_path, max_results, detected_category, detected_category)
                results["search_results"].append({
                    "source_image": image_path,
                    "detected_category": detected_category,
                    "category_confidence": image_analysis.get("confidence", 0.0),
                    "similar_images": similar_images,
                    "found_count": len(similar_images)
                })
            except Exception as e:
                logging.error(f"Failed to search similar images for {image_path}: {e}")
                results["search_results"].append({
                    "source_image": image_path,
                    "error": str(e),
                    "similar_images": []
                })

        return results

    def _search_similar_images_web(self, image_path: str, max_results: int, detected_category: str = "unknown", search_query: str = "") -> List[Dict[str, Any]]:
        """Search for similar images using web services."""
        # This is a placeholder implementation
        # In a real implementation, this would use:
        # - Google Images API
        # - Bing Image Search API
        # - Computer vision services (Azure, AWS, etc.)
        # - Reverse image search services

        # For now, return mock results with diverse real image URLs
        # In a real implementation, this would analyze the uploaded image and return similar images
        mock_results = []
        diverse_images = [
            # Technology/Computers
            {
                "url": "https://images.unsplash.com/photo-1518709268805-4e9042ac2176?w=400",
                "title": "Modern Laptop on Desk",
                "dimensions": "800x600",
                "category": "technology"
            },
            {
                "url": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400",
                "title": "Smartphone with Apps",
                "dimensions": "1024x768",
                "category": "technology"
            },
            # Nature/Landscapes
            {
                "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
                "title": "Mountain Landscape",
                "dimensions": "640x480",
                "category": "nature"
            },
            {
                "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400",
                "title": "Forest Path",
                "dimensions": "720x540",
                "category": "nature"
            },
            # Food/Cooking
            {
                "url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400",
                "title": "Fresh Salad Bowl",
                "dimensions": "600x800",
                "category": "food"
            },
            {
                "url": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400",
                "title": "Coffee and Pastries",
                "dimensions": "800x600",
                "category": "food"
            },
            # Architecture/Buildings
            {
                "url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400",
                "title": "Modern Building",
                "dimensions": "1024x768",
                "category": "architecture"
            },
            {
                "url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400",
                "title": "City Skyline",
                "dimensions": "640x480",
                "category": "architecture"
            },
            # People/Portraits
            {
                "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
                "title": "Person Portrait",
                "dimensions": "720x540",
                "category": "people"
            },
            {
                "url": "https://images.unsplash.com/photo-1494790108755-2a719461b786?w=400",
                "title": "Professional Headshot",
                "dimensions": "600x800",
                "category": "people"
            },
            # Animals (including dogs)
            {
                "url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
                "title": "Golden Retriever in Park",
                "dimensions": "800x600",
                "category": "animals"
            },
            {
                "url": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400",
                "title": "Labrador Retriever Portrait",
                "dimensions": "1024x768",
                "category": "animals"
            },
            {
                "url": "https://images.unsplash.com/photo-1544568100-847a948585b9?w=400",
                "title": "Cat on Windowsill",
                "dimensions": "720x540",
                "category": "animals"
            },
            {
                "url": "https://images.unsplash.com/photo-1444464666168-49d633b86797?w=400",
                "title": "Bird in Nature",
                "dimensions": "600x800",
                "category": "animals"
            },
            # Transportation/Vehicles
            {
                "url": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=400",
                "title": "Red Sports Car",
                "dimensions": "800x600",
                "category": "transportation"
            },
            {
                "url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400",
                "title": "Motorcycle",
                "dimensions": "1024x768",
                "category": "transportation"
            }
        ]

        # Get historical ratings for learning
        historical_ratings = {}
        try:
            import db
            database = db.Database("./data/research.db")

            # Get ratings for the detected category
            if detected_category != "unknown":
                category_ratings = database.get_image_ratings_for_category(detected_category, limit=50)
                for rating in category_ratings:
                    url = rating['image_url']
                    historical_ratings[url] = rating['rating']
        except Exception as e:
            logging.warning(f"Could not load historical ratings: {e}")

        # Score and prioritize images based on category and historical ratings
        scored_images = []

        for image in diverse_images:
            score = 0.0

            # Category matching bonus
            if image["category"] == detected_category:
                score += 100.0  # Major boost for same category

            # Historical rating bonus
            image_url = image["url"]
            if image_url in historical_ratings:
                if historical_ratings[image_url] == "up":
                    score += 50.0  # Previously liked images get boost
                else:
                    score -= 30.0  # Previously disliked images get penalty

            # Base score for variety
            score += 10.0

            scored_images.append((score, image))

        # Sort by score (highest first) and select top images
        scored_images.sort(key=lambda x: x[0], reverse=True)
        selected_images = [img for score, img in scored_images[:max_results]]

        for i, image_data in enumerate(selected_images):
            # Higher similarity scores for same category matches
            base_similarity = 0.85 if image_data["category"] == detected_category else 0.65
            similarity_score = base_similarity - (i * 0.05)

            mock_results.append({
                "url": image_data["url"],
                "thumbnail_url": image_data["url"].replace("?w=400", "?w=100"),
                "title": image_data["title"],
                "source": f"Unsplash ({image_data['category'].title()})",
                "similarity_score": max(0.1, similarity_score),  # Ensure minimum similarity
                "dimensions": image_data["dimensions"],
                "category": image_data["category"],
                "matched_category": image_data["category"] == detected_category,
                "requires_rating": True
            })

        return mock_results

    def process_image_ratings(self, image_ratings: Dict[str, Any]) -> Dict[str, Any]:
        """Process user ratings for similar images."""
        processed_ratings = {
            "total_ratings": len(image_ratings),
            "thumbs_up": 0,
            "thumbs_down": 0,
            "rating_distribution": {},
            "processed_timestamp": datetime.now().isoformat()
        }

        for image_id, rating in image_ratings.items():
            if rating == "up":
                processed_ratings["thumbs_up"] += 1
            elif rating == "down":
                processed_ratings["thumbs_down"] += 1

        processed_ratings["rating_distribution"] = {
            "positive": processed_ratings["thumbs_up"],
            "negative": processed_ratings["thumbs_down"],
            "neutral": processed_ratings["total_ratings"] - processed_ratings["thumbs_up"] - processed_ratings["thumbs_down"]
        }

        return processed_ratings