"""
seed_data.py  — Populates the database with your habits and completed book list.
Run once: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import database as db

db.init_db()

# ── HABITS ────────────────────────────────────────────────────────────────────
HABITS = [
    # (name, category, description, action_type, unit, target_value)
    ("Black Coffee", "Morning Ritual", "Morning ritual with black coffee", "checkbox", None, None),
    ("Left Hand Writing", "Brain Training", "Practice writing with left hand", "quantity", "pages", 2),
    ("Left Hand Mirror Writing", "Brain Training", "Practice mirror writing with left hand", "quantity", "pages", 2),
    ("Duolingo", "Learning", "Language learning app", "quantity", "lessons", 1),
    ("Mental Models Study", "Learning", "Study & proof-read mental models", "pages", "pages", 20),
    ("Read from Project Holistic", "Learning", "Reading pages from project books", "pages", "pages", 50),
    ("Wisdom Wellbeing", "Wellbeing", "Ideation for motivating/energizing ideas", "quantity", "ideas", 3),
    ("Finance Vital-Check", "Finance", "Review financial health metrics", "checkbox", None, None),
    ("Clean Eating", "Health", "Eat healthy, unprocessed foods", "checkbox", None, None),
    ("Gym", "Health", "Strength training or gym workout", "duration", "hours", 1.0),
    ("Cook Lunch", "Health", "Cook nutritious lunch", "checkbox", None, None),
    ("Walking", "Health", "Take a walk or active movement", "duration", "hours", 0.5),
    ("Daily Journal", "Reflection", "Reflect and journal each day", "duration", "minutes", 15),
]

print("Seeding habits...")
for name, cat, desc, action_type, unit, target in HABITS:
    db.create_habit(name, cat, desc, action_type, unit, target)
    print(f"  + {name} ({action_type})")

# ── COMPLETED BOOKS ───────────────────────────────────────────────────────────
COMPLETED_BOOKS = [
    (1,  "The Stoic Mind",                                         "Philosophy",                "Addy Osmoni",          "2024"),
    (2,  "How to Talk to Anyone",                                  "Persuasion",                "Leil Lowndes",         "2024"),
    (3,  "Steal Like an Artist",                                   "Creativity",                "Austin Kleon",         "2024"),
    (4,  "Atomic Habits",                                          "Habit creation",            "James Clear",          "2024, 2025"),
    (5,  "Four Agreements",                                        "Philosophy",                "Don Miguel Ruiz",      "2024"),
    (6,  "Strangest Secret",                                       "Philosophy",                "Earl Nightingale",     "2024"),
    (7,  "Decision Book",                                          "Decision making",           "Mikael Krogerus",      "2024"),
    (8,  "The Question Book",                                      "Fun Read",                  "Mikael Krogerus",      "2024"),
    (9,  "Meditations",                                            "Philosophy",                "Marcus Aurelius",      "2024; 2025"),
    (10, "Wisdom Theory",                                          "Mental Models",             "Vibatsu",              "2025; 2026"),
    (11, "Seeking Wisdom",                                         "Mental Models",             "Peter Bevelin",        "2025; 2026"),
    (12, "38 Letters from John D. Rockefeller to his Son",         "Letter",                    "Rockefeller",          "2025"),
    (13, "What Are You Doing with Your Life",                      "Philosophy",                "J. Krishnamurti",      "2025; 2026"),
    (14, "Life of an Entrepreneur",                                "Entrepreneurship",          "Patrick Bet-David",    "2024"),
    (15, "Bed of Procrustes",                                      "Philosophy",                "Nassim Nicholas Taleb","2024"),
    (16, "Surrounded by Idiots",                                   "Psychology",                "Thomas Erikson",       "2024"),
    (17, "Fat Chance",                                             "Nutrition and Biochemistry","Robert Lustig",        "2025"),
    (18, "Thank You for Being Late",                               "Philosophy",                "Thomas L. Friedman",   ""),
    (19, "Show Your Work",                                         "Creativity",                "Austin Kleon",         "2024"),
    (20, "Diary of a CEO",                                         "Business",                  "Steven Bartlett",      "2025"),
    (21, "The Coming Wave",                                        "Technology",                "Mustafa Suleyman",     "2025"),
    (22, "Building a Second Brain",                                "Productivity",              "Tiago Forte",          "2024"),
    (23, "30 Lessons for Living",                                  "Wisdom",                    "Karl Pillemer",        ""),
    (24, "Visual Intelligence",                                    "Intelligence",              "Amy E. Herman",        ""),
    (25, "101 Essays That Will Change the Way You Think",          "Relaxation",                "Brianna Wiest",        ""),
    (26, "Start with Why",                                         "Idea formulation",          "Simon Sinek",          "2024"),
    (27, "Hackers and Painters",                                   "Founder mentality",         "Paul Graham",          ""),
    (28, "Everybody Writes",                                       "Writing",                   "Ann Handley",          "2025"),
    (29, "Almanack of Naval Ravikant",                             "Mindset",                   "Eric Jorgenson",       "2025"),
    (30, "Anthology of Balaji",                                    "Mindset",                   "Eric Jorgenson",       "2025"),
    (31, "48 Laws of Power",                                       "Power Dynamics",            "Robert Greene",        "2024"),
    (32, "Art of Seduction",                                       "Psychology",                "Robert Greene",        "2024"),
    (33, "The Compound Effect",                                    "Compounding",               "Darren Hardy",         "2024"),
    (34, "The One Thing",                                          "Business Wisdom",           "Gary Keller",          ""),
    (35, "Zero to One",                                            "Business Wisdom",           "Peter Thiel",          "2024"),
    (36, "The Prince",                                             "Psychology",                "Machiavelli",          ""),
    (37, "The Hard Thing About Hard Things",                       "Business Wisdom",           "Ben Horowitz",         "2024"),
    (38, "$100M Offers",                                           "Business Wisdom",           "Alex Hormozi",         "2025"),
    (39, "The Art of War",                                         "War Strategy",              "Sun Tzu",              "2024"),
    (40, "The Lean Startup",                                       "Business Wisdom",           "Eric Ries",            "2024"),
    (41, "Business of the 21st Century",                           "Business Investing",        "Robert Kiyosaki",      "2024"),
    (42, "Rich Dad Poor Dad",                                      "Business Investing",        "Robert Kiyosaki",      "2024"),
    (43, "The Go-Giver",                                           "Business",                  "Bob Burg",             "2024"),
    (44, "Find Your Why",                                          "Business Ideation",         "Simon Sinek",          ""),
    (45, "Poor Charlie's Almanack",                                "Wisdom",                    "Peter Kaufman",        "2025; 2026"),
    (46, "On Writing Well",                                        "Writing",                   "William Zinsser",      "2025"),
    (47, "Psycho-Cybernetics",                                     "Psychology",                "Maxwell Maltz",        "2024"),
    (48, "The Psychology of Money",                                "Personal Finance",          "Morgan Housel",        "2025"),
    (49, "Behave: The Biology of Humans at Our Best and Worst",    "Behavioural Biology",       "Robert M. Sapolsky",   ""),
    (50, "Biohack Your Brain",                                     "Biohacking",                "Kristen Willeumier",   ""),
    (51, "Limitless",                                              "Biohacking",                "Jim Kwik",             ""),
    (52, "Moonwalking with Einstein",                              "Relaxation",                "Joshua Foer",          ""),
    (53, "The Rudest Book Ever",                                   "Relaxation",                "Shwetabh Gangwar",     ""),
    (54, "All I Want to Know Is Where I'm Going to Die (So I'll Never Go There)", "Wisdom",   "Peter Bevelin",        "2025"),
    (55, "Great Mental Models Volume 1",                           "Mental Models",             "Shane Parrish",        "2025"),
    (56, "Great Mental Models Volume 2: Physics, Chemistry, Biology","Mental Models",           "Shane Parrish",        "2025"),
    (57, "59 Seconds",                                             "Psychology",                "Richard Wiseman",      "2025"),
    (58, "Where Good Ideas Come From",                             "Creativity",                "Steven Johnson",       "2025"),
    (59, "Outlive",                                                "Longevity",                 "Peter Attia",          "2024"),
    (60, "The Vital Question",                                     "Evolutionary Biochemistry", "Nick Lane",            "2025"),
    (61, "Quantum Biology and Biochemistry",                       "Nutrition and Biochemistry","Brian Fertig",         "2025"),
    (62, "Quantum Biology and Metabolism",                         "Nutrition and Biochemistry","Brian Fertig",         "2025"),
    (63, "Seneca: Letters to Lucilius",                            "Philosophy",                "Seneca",               "2025"),
    (64, "Dirty Genes",                                            "Gene and Nutrition",        "Ben Lynch",            "2025"),
    (65, "Sugar: The Bitter Truth",                                "Nutrition and Biochemistry","Robert Lustig",        "2024"),
    (66, "How to Take a Chance",                                   "Probability",               "Darrel Huff",          "2025"),
    (67, "The Fat Switch",                                         "Kidney Biochemistry",       "Richard Johnson",      "2024"),
    (68, "Nature Wants Us to Be Fat",                              "Multi-Factorial Disorders", "Richard Johnson",      "2024"),
    (69, "The Sugar Fix",                                          "Multi-Factorial Disorders", "Richard Johnson",      "2024"),
    (70, "Personal MBA",                                           "MBA",                       "Josh Kaufman",         "2024"),
    (71, "The Psychology of Spending Money",                       "Money Psychology",          "Morgan Housel",        "2025"),
    (72, "Range",                                                  "Generalist Approach",       "David Epstein",        "2025"),
    (73, "The Little Prince",                                      "Fiction",                   "Antoine de Saint-Exupéry","2025"),
    (74, "Mastery",                                                "Personal Development",      "Robert Greene",        "2025"),
    (75, "What Every Body Is Saying",                              "Non-Verbal Behaviour",      "Joe Navarro",          "2024"),
    (76, "Never Split the Difference",                             "Negotiation",               "Chris Voss",           "2025"),
    (77, "The Tipping Point",                                      "Psychology",                "Malcolm Gladwell",     "2024"),
    (78, "Learn Like a Polymath",                                  "Polymath Skills",           "Peter Hollins",        "2025"),
    (79, "Build Don't Talk",                                       "Business",                  "Raj Shamani",          "2024"),
    (80, "Talking to Humans",                                      "Customer Acquisition",      "Giff Constable",       "2025"),
    (81, "Testing with Humans",                                    "Experimentation",           "Giff Constable",       "2025"),
    (82, "The Product Book",                                       "Product Thinking",          "Product School",       "2025"),
    (83, "Million Dollar Weekend",                                 "Audacious Move",            "Noah Kagan",           "2025"),
]

print("Seeding completed books...")
for row in COMPLETED_BOOKS:
    _, title, discipline, author, year_read = row
    db.add_book(
        title=title, author=author, discipline=discipline,
        status="Completed", year_read=year_read
    )
    print(f"  + [{_:02d}] {title}")

# ── CURRENTLY READING (from image) ───────────────────────────────────────────
INPROGRESS_BOOKS = [
    ("Seeking Wisdom",                "Multi-Disciplinary Thinking",  "Peter Bevelin",    "The Physics and Mathematics of Misjudgements"),
    ("Principles by Ray Dalio",       "Philosophical Investment",      "Ray Dalio",        "Part 1 - Where I'm Coming From"),
    ("Personal MBA by Josh Kaufman",  "Business Creation",             "Josh Kaufman",     "Value Creation - 25 concepts remaining"),
    ("Read All Ideations",            "Retrospect for 2025",           "",                 ""),
    ("Thyroid Solution",              "Medicine",                      "",                 "Intermittent Read"),
    ("Charlie Munger: A Complete Investor","Mentor",                   "",                 "Chapter 1"),
    ("Leonardo Da Vinci Biography",   "Mentor",                        "Walter Isaacson",  "Chapter 1"),
    ("Spark of the Genius",           "Mentor",                        "",                 "Intermittent Read"),
    ("Think Like Da Vinci",           "Creativity",                    "Michael Gelb",     ""),
    ("An Introduction to Cybernetics","Systems Thinking",              "Ashby",            ""),
    ("An Introduction to Systems Biology","Systems Biology",           "Uri Alon",         ""),
    ("Scale",                         "Biology",                       "Geoffrey West",    ""),
    ("At Home in the Universe",       "Complexity",                    "Stuart Kauffman",  ""),
    ("Cybernetics",                   "Systems Thinking",              "",                 ""),
    ("Zero Module - Fundamental Analysis","Finance",                   "",                 ""),
    ("Deep Medicine",                 "Biology",                       "",                 "Chapter 2"),
]

# On hold
ON_HOLD_BOOKS = [
    ("Charlie Munger: A Complete Investor", "Mentor", "", "Hold"),
    ("Surely You're Joking, Mr. Feynman",   "Mentor", "Richard Feynman", ""),
]

# Yet to start
YET_TO_START_BOOKS = [
    ("Epigenetic Revolution",          "Biology",  "", "Feb-26"),
    ("Perfect Deviations by Richard Feynman","Mentor","","Jan-26"),
]

print("Seeding in-progress books...")
for title, discipline, author, activity in INPROGRESS_BOOKS:
    db.add_book(title=title, author=author, discipline=discipline,
                status="Inprogress", activity=activity)
    print(f"  + {title}")

print("Seeding on-hold books...")
for title, discipline, author, activity in ON_HOLD_BOOKS:
    db.add_book(title=title, author=author, discipline=discipline,
                status="On Hold", activity=activity)
    print(f"  + {title}")

print("Seeding yet-to-start books...")
for title, discipline, author, activity in YET_TO_START_BOOKS:
    db.add_book(title=title, author=author, discipline=discipline,
                status="Yet To Start", activity=activity)
    print(f"  + {title}")

print("\n✅ Seed complete!")
print(f"  Habits:  {len(HABITS)}")
print(f"  Books:   {len(COMPLETED_BOOKS) + len(INPROGRESS_BOOKS) + len(ON_HOLD_BOOKS) + len(YET_TO_START_BOOKS)}")
