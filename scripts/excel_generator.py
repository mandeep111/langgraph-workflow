import os
from config import Config
import pandas as pd
from datetime import datetime
from typing import List, Dict

class ExcelGenerator:
    def load_existing_articles(self) -> pd.DataFrame:
        """Load existing articles from Excel file"""
        try:
            if os.path.exists(Config.EXCEL_FILE_PATH):
                df = pd.read_excel(Config.EXCEL_FILE_PATH)
                # Ensure required columns exist
                if 'status' not in df.columns:
                    df['status'] = False
                if 'video_created' not in df.columns:
                    df['video_created'] = False
                if 'created_date' not in df.columns:
                    df['created_date'] = datetime.now().strftime('%Y-%m-%d')
                return df
            else:
                # Create empty DataFrame with required columns
                return pd.DataFrame(columns=[
                    'title', 'summary', 'url', 'source', 'date', 'category',
                    'enhanced_summary', 'importance', 'image_keywords',
                    'status', 'video_created', 'created_date'
                ])
        except Exception as e:
            print(f"Error loading existing articles: {e}")
            return pd.DataFrame(columns=[
                'title', 'summary', 'url', 'source', 'date', 'category',
                'enhanced_summary', 'importance', 'image_keywords',
                'status', 'video_created', 'created_date'
            ])
    
    def filter_new_articles(self, new_articles: List[Dict], existing_df: pd.DataFrame) -> List[Dict]:
        """Filter out articles that already exist in the database"""
        if existing_df.empty:
            return new_articles
        
        existing_urls = set(existing_df['url'].tolist())
        existing_titles = set(existing_df['title'].tolist())
        
        filtered_articles = []
        for article in new_articles:
            # Check if article already exists by URL or title
            if article['url'] not in existing_urls and article['title'] not in existing_titles:
                filtered_articles.append(article)
        
        print(f"📊 Found {len(new_articles)} total articles, {len(filtered_articles)} are new")
        return filtered_articles
    
    def get_unprocessed_articles(self, existing_df: pd.DataFrame, limit: int = 5) -> List[Dict]:
        """Get articles that haven't been processed for video creation"""
        if existing_df.empty:
            return []
        
        # Filter articles where video_created is False
        unprocessed = existing_df[existing_df['video_created'] == False].copy()
        
        # Sort by importance and date
        if 'importance' in unprocessed.columns:
            unprocessed = unprocessed.sort_values(['importance', 'date'], ascending=[False, False])
        
        # Limit the number of articles
        unprocessed = unprocessed.head(limit)
        
        return unprocessed.to_dict('records')
    
    def create_or_update_excel_report(self, new_articles: List[Dict]) -> str:
        """Create or update the persistent Excel report"""
        try:
            # Load existing data
            existing_df = self.load_existing_articles()
            
            # Filter new articles
            filtered_articles = self.filter_new_articles(new_articles, existing_df)
            
            if filtered_articles:
                # Convert new articles to DataFrame
                new_df = pd.DataFrame(filtered_articles)
                
                # Add status columns for new articles
                new_df['status'] = False
                new_df['video_created'] = False
                new_df['created_date'] = datetime.now().strftime('%Y-%m-%d')
                
                # Combine with existing data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = existing_df
            
            # Save to Excel
            with pd.ExcelWriter(Config.EXCEL_FILE_PATH, engine='openpyxl') as writer:
                combined_df.to_excel(writer, sheet_name='AI_Tech_News', index=False)
                
                # Format the worksheet
                worksheet = writer.sheets['AI_Tech_News']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"📊 Excel database updated: {Config.EXCEL_FILE_PATH}")
            print(f"📈 Total articles in database: {len(combined_df)}")
            print(f"🆕 New articles added: {len(filtered_articles) if filtered_articles else 0}")
            
            return Config.EXCEL_FILE_PATH
            
        except Exception as e:
            print(f"Error updating Excel report: {e}")
            return ""
    
    def mark_articles_as_processed(self, article_titles: List[str]):
        """Mark articles as processed (video created)"""
        try:
            if os.path.exists(Config.EXCEL_FILE_PATH):
                df = pd.read_excel(Config.EXCEL_FILE_PATH)
                
                # Mark articles as processed
                for title in article_titles:
                    mask = df['title'] == title
                    df.loc[mask, 'video_created'] = True
                    df.loc[mask, 'status'] = True
                
                # Save updated data
                with pd.ExcelWriter(Config.EXCEL_FILE_PATH, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='AI_Tech_News', index=False)
                
                print(f"✅ Marked {len(article_titles)} articles as processed")
        except Exception as e:
            print(f"Error marking articles as processed: {e}")
