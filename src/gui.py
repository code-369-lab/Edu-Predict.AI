import pygame
import sys
from src.prediction import StudentPredictor
class StudentPerformanceGUI:
    def __init__(self):
        pygame.init()
        
        # Screen settings
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Student Performance Prediction System")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (41, 128, 185)
        self.LIGHT_BLUE = (52, 152, 219)
        self.GREEN = (46, 204, 113)
        self.RED = (231, 76, 60)
        self.GRAY = (189, 195, 199)
        self.LIGHT_GRAY = (236, 240, 241)
        self.DARK_GRAY = (52, 73, 94)
        self.YELLOW = (241, 196, 15)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.label_font = pygame.font.Font(None, 28)
        self.input_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Predictor
        self.predictor = StudentPredictor()
        
        # Input fields
        self.inputs = {
            'age': {'value': '18', 'active': False, 'rect': None, 'type': 'int'},
            'gender': {'value': 'M', 'active': False, 'rect': None, 'type': 'choice', 'options': ['M', 'F']},
            'study_hours': {'value': '5.0', 'active': False, 'rect': None, 'type': 'float'},
            'attendance': {'value': '85.0', 'active': False, 'rect': None, 'type': 'float'},
            'previous_grade': {'value': '75.0', 'active': False, 'rect': None, 'type': 'float'},
            'parent_education': {'value': 'bachelor', 'active': False, 'rect': None, 'type': 'choice', 
                               'options': ['high_school', 'bachelor', 'master', 'phd']},
            'internet_access': {'value': '1', 'active': False, 'rect': None, 'type': 'choice', 'options': ['0', '1']},
            'family_support': {'value': '1', 'active': False, 'rect': None, 'type': 'choice', 'options': ['0', '1']},
            'extra_curricular': {'value': '1', 'active': False, 'rect': None, 'type': 'choice', 'options': ['0', '1']},
            'sleep_hours': {'value': '7.0', 'active': False, 'rect': None, 'type': 'float'},
            'tutoring': {'value': '0', 'active': False, 'rect': None, 'type': 'choice', 'options': ['0', '1']}
        }
        
        # Buttons
        self.predict_button = None
        self.clear_button = None
        
        # Results
        self.predicted_grade = None
        self.performance_category = None
        self.recommendations = []
        
        self.clock = pygame.time.Clock()
    
    def draw_text(self, text, font, color, x, y, center=False):
        """Draw text on screen"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def draw_input_field(self, label, key, x, y, width=200):
        """Draw input field"""
        # Label
        self.draw_text(label, self.label_font, self.DARK_GRAY, x, y)
        
        # Input box
        input_data = self.inputs[key]
        color = self.BLUE if input_data['active'] else self.GRAY
        rect = pygame.Rect(x, y + 35, width, 40)
        input_data['rect'] = rect
        
        pygame.draw.rect(self.screen, color, rect, 2, border_radius=5)
        pygame.draw.rect(self.screen, self.WHITE, rect.inflate(-4, -4), border_radius=5)
        
        # Display value
        value_text = str(input_data['value'])
        if input_data['type'] == 'choice':
            # Show options for choice fields
            value_text = f"{input_data['value']} ▼"
        
        self.draw_text(value_text, self.input_font, self.BLACK, x + 10, y + 45)
        
        return rect
    
    def draw_button(self, text, x, y, width, height, color, hover_color):
        """Draw button"""
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, width, height)
        
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, hover_color, rect, border_radius=10)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
        
        self.draw_text(text, self.label_font, self.WHITE, x + width // 2, y + height // 2, center=True)
        return rect
    
    def draw_result_card(self):
        """Draw prediction result card"""
        if self.predicted_grade is None:
            return
        
        # Result card background
        card_rect = pygame.Rect(750, 150, 400, 250)
        pygame.draw.rect(self.screen, self.WHITE, card_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.BLUE, card_rect, 3, border_radius=15)
        
        # Title
        self.draw_text("Prediction Result", self.title_font, self.BLUE, 950, 180, center=True)
        
        # Grade
        grade_text = f"Grade: {self.predicted_grade:.1f}/100"
        self.draw_text(grade_text, self.label_font, self.BLACK, 950, 240, center=True)
        
        # Category with color
        category_colors = {
            'Poor': self.RED,
            'Average': self.YELLOW,
            'Good': self.LIGHT_BLUE,
            'Excellent': self.GREEN
        }
        category_color = category_colors.get(self.performance_category, self.BLACK)
        
        category_text = f"Category: {self.performance_category}"
        self.draw_text(category_text, self.label_font, category_color, 950, 280, center=True)
        
        # Grade bar
        bar_width = 300
        bar_height = 30
        bar_x = 800
        bar_y = 330
        
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=15)
        
        grade_width = int((self.predicted_grade / 100) * bar_width)
        pygame.draw.rect(self.screen, category_color, (bar_x, bar_y, grade_width, bar_height), border_radius=15)
        
        # Percentage
        self.draw_text(f"{self.predicted_grade:.1f}%", self.input_font, self.WHITE, 
                      bar_x + grade_width - 50, bar_y + 5)
    
    def draw_recommendations(self):
        """Draw recommendations"""
        if not self.recommendations:
            return
        
        # Recommendations card
        card_rect = pygame.Rect(750, 420, 400, 350)
        pygame.draw.rect(self.screen, self.WHITE, card_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.GREEN, card_rect, 3, border_radius=15)
        
        # Title
        self.draw_text("Recommendations", self.label_font, self.GREEN, 950, 440, center=True)
        
        # Recommendations list
        y_offset = 480
        for i, rec in enumerate(self.recommendations[:5]):  # Show max 5 recommendations
            # Wrap text if too long
            if len(rec) > 45:
                rec = rec[:42] + "..."
            
            self.draw_text(rec, self.small_font, self.DARK_GRAY, 770, y_offset)
            y_offset += 30
    
    def draw_ui(self):
        """Draw complete UI"""
        self.screen.fill(self.LIGHT_GRAY)
        
        # Header
        header_rect = pygame.Rect(0, 0, self.WIDTH, 100)
        pygame.draw.rect(self.screen, self.BLUE, header_rect)
        self.draw_text("Student Performance Prediction System", self.title_font, 
                      self.WHITE, self.WIDTH // 2, 50, center=True)
        
        # Input section title
        self.draw_text("Student Information", self.label_font, self.DARK_GRAY, 50, 120)
        
        # Input fields - Left column
        y_pos = 170
        left_col = 50
        
        self.draw_input_field("Age:", 'age', left_col, y_pos)
        self.draw_input_field("Gender (M/F):", 'gender', left_col, y_pos + 100)
        self.draw_input_field("Study Hours/Day:", 'study_hours', left_col, y_pos + 200)
        self.draw_input_field("Attendance %:", 'attendance', left_col, y_pos + 300)
        self.draw_input_field("Previous Grade:", 'previous_grade', left_col, y_pos + 400)
        
        # Input fields - Middle column
        mid_col = 350
        self.draw_input_field("Parent Education:", 'parent_education', mid_col, y_pos, width=250)
        self.draw_input_field("Internet (0/1):", 'internet_access', mid_col, y_pos + 100)
        self.draw_input_field("Family Support (0/1):", 'family_support', mid_col, y_pos + 200)
        self.draw_input_field("Extra-curricular (0/1):", 'extra_curricular', mid_col, y_pos + 300)
        self.draw_input_field("Sleep Hours:", 'sleep_hours', mid_col, y_pos + 400)
        self.draw_input_field("Tutoring (0/1):", 'tutoring', mid_col, y_pos + 500)
        
        # Buttons
        self.predict_button = self.draw_button("Predict Performance", 100, 720, 200, 50, 
                                               self.GREEN, self.LIGHT_BLUE)
        self.clear_button = self.draw_button("Clear", 350, 720, 150, 50, 
                                            self.RED, self.YELLOW)
        
        # Results
        self.draw_result_card()
        self.draw_recommendations()
        
        # Footer
        self.draw_text("Click on fields to edit • Use choice fields dropdown", 
                      self.small_font, self.DARK_GRAY, self.WIDTH // 2, 780, center=True)
    
    def handle_input_click(self, pos):
        """Handle click on input fields"""
        for key, input_data in self.inputs.items():
            if input_data['rect'] and input_data['rect'].collidepoint(pos):
                # Deactivate all others
                for k in self.inputs:
                    self.inputs[k]['active'] = False
                
                # Activate clicked field
                input_data['active'] = True
                
                # For choice fields, cycle through options
                if input_data['type'] == 'choice':
                    current_idx = input_data['options'].index(input_data['value'])
                    next_idx = (current_idx + 1) % len(input_data['options'])
                    input_data['value'] = input_data['options'][next_idx]
    
    def handle_keyboard(self, event):
        """Handle keyboard input"""
        for key, input_data in self.inputs.items():
            if input_data['active'] and input_data['type'] != 'choice':
                if event.key == pygame.K_BACKSPACE:
                    input_data['value'] = input_data['value'][:-1]
                elif event.key == pygame.K_RETURN:
                    input_data['active'] = False
                else:
                    # Only allow valid characters based on type
                    if input_data['type'] == 'int' and event.unicode.isdigit():
                        input_data['value'] += event.unicode
                    elif input_data['type'] == 'float' and (event.unicode.isdigit() or event.unicode == '.'):
                        if event.unicode == '.' and '.' in input_data['value']:
                            continue
                        input_data['value'] += event.unicode
                    elif input_data['type'] == 'choice':
                        pass  # Handled by click
    
    def validate_inputs(self):
        """Validate all inputs"""
        try:
            student_data = {}
            
            for key, input_data in self.inputs.items():
                value = input_data['value']
                
                if input_data['type'] == 'int':
                    student_data[key] = int(value) if value else 0
                elif input_data['type'] == 'float':
                    student_data[key] = float(value) if value else 0.0
                elif input_data['type'] == 'choice':
                    if key == 'gender':
                        student_data[key] = value
                    elif key == 'parent_education':
                        student_data[key] = value
                    else:
                        student_data[key] = int(value)
            
            return student_data, True
        except ValueError as e:
            print(f"Validation error: {e}")
            return None, False
    
    def predict(self):
        """Make prediction"""
        student_data, valid = self.validate_inputs()
        
        if not valid:
            print("Invalid input data")
            return
        
        grade, category = self.predictor.predict_grade(student_data)
        
        if grade:
            self.predicted_grade = grade
            self.performance_category = category
            self.recommendations = self.predictor.get_recommendations(student_data, grade)
        else:
            print(f"Prediction failed: {category}")
    
    def clear_inputs(self):
        """Clear all inputs and results"""
        self.inputs = {
            'age': {'value': '18', 'active': False, 'rect': None, 'type': 'int'},
            'gender': {'value': 'M', 'active': False, 'rect': None, 'type': 'choice', 'options': ['M', 'F']},
            'study_hours': {'value': '5.0', 'active': False, 'rect': None, 'type': 'float'},
            'attendance': {'value': '85.0', 'active': False, 'rect': None, 'type': 'float'},
            'previous_grade': {'value': '75.0', 'active': False, 'rect': None, 'type': 'float'},
            'parent_education': {'value': 'bachelor', 'active': False, 'rect': None, 'type': 'choice', 
                               'options': ['high_school', 'bachelor', 'master', 'phd']},
            'internet_access': {'value': '1', 'active': False, 'rect': None, 'type': 'choice', 'options': ['0', '1']},
            'family_support': {'value': '1', 'active': False, 'rect': None, 'type': 'choice', 'options': ['0', '1']},
            'extra_curricular': {'value': '1', 'active': False, 'rect': None, 'type': 'choice', 'options': ['0', '1']},
            'sleep_hours': {'value': '7.0', 'active': False, 'rect': None, 'type': 'float'},
            'tutoring': {'value': '0', 'active': False, 'rect': None, 'type': 'choice', 'options': ['0', '1']}
        }
        
        self.predicted_grade = None
        self.performance_category = None
        self.recommendations = []
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Check input fields
                    self.handle_input_click(pos)
                    
                    # Check predict button
                    if self.predict_button and self.predict_button.collidepoint(pos):
                        self.predict()
                    
                    # Check clear button
                    if self.clear_button and self.clear_button.collidepoint(pos):
                        self.clear_inputs()
                
                if event.type == pygame.KEYDOWN:
                    self.handle_keyboard(event)
            
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gui = StudentPerformanceGUI()
    gui.run()