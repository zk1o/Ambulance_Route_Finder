# data/network_data.py

# 1. مواقع العقد وإحداثياتها (X, Y) لحساب Euclidean Distance للـ A* Heuristic
NODES_COORDINATES = {
    'Ambulance_Base': (0, 2),
    'Emergency_Site': (10, 4),
    'Hospital_A': (6, 6),
    'Hospital_B': (13, 11),
    'Hospital_C': (16, 2),
    'Node_1': (0, 0),   'Node_2': (2, 3),   'Node_3': (5, 2),
    'Node_4': (8, 5),   'Node_5': (1, 7),   'Node_6': (4, 8),
    'Node_7': (9, 9),   'Node_8': (12, 6),  'Node_9': (15, 8),
    'Node_10': (3, 12), 'Node_11': (7, 13), 'Node_12': (11, 12),
    'Node_13': (14, 14),'Node_14': (18, 10),'Node_15': (17, 4)
}

# 2. شبكة الطرق: (العقدة_الأولى, العقدة_الثانية, المسافة_كم, السرعة_الأساسية_كم/س, هل_هو_مسار_طوارئ)
ROADS_NETWORK = [
    ('Ambulance_Base', 'Node_1', 2.0, 50, False),
    ('Ambulance_Base', 'Node_2', 3.5, 60, True),
    ('Node_1', 'Node_2', 2.5, 40, False),
    ('Node_1', 'Node_5', 7.0, 80, True),
    ('Node_2', 'Node_3', 4.0, 50, False),
    ('Node_2', 'Node_6', 5.5, 60, False),
    ('Node_3', 'Hospital_A', 3.0, 50, False),
    ('Node_3', 'Emergency_Site', 6.0, 70, True),
    ('Node_4', 'Emergency_Site', 2.5, 50, False),
    ('Node_4', 'Hospital_A', 3.0, 60, False),
    ('Node_5', 'Node_6', 3.0, 50, False),
    ('Node_5', 'Node_10', 6.0, 70, True),
    ('Node_6', 'Hospital_A', 4.0, 50, False),
    ('Node_6', 'Node_11', 5.0, 60, False),
    ('Emergency_Site', 'Node_8', 3.0, 50, False),
    ('Emergency_Site', 'Node_15', 7.0, 80, True),
    ('Node_8', 'Node_15', 4.5, 60, False),
    ('Node_8', 'Hospital_B', 5.0, 70, True),
    ('Hospital_A', 'Node_11', 6.0, 60, False),
    ('Node_11', 'Node_12', 4.0, 50, False),
    ('Node_12', 'Hospital_B', 3.0, 60, False),
    ('Node_12', 'Node_13', 4.0, 60, False),
    ('Hospital_B', 'Node_13', 3.5, 50, False),
    ('Node_13', 'Node_14', 5.0, 70, True),
    ('Node_15', 'Hospital_C', 3.0, 60, False),
    ('Node_14', 'Hospital_C', 6.0, 60, False),
    ('Node_14', 'Node_9', 4.0, 50, False),
    ('Node_9', 'Node_12', 5.0, 60, False),
    ('Node_3', 'Node_4', 4.5, 50, False),
    ('Node_4', 'Node_8', 4.5, 60, False),
    ('Node_4', 'Node_7', 4.5, 50, False),
    ('Node_7', 'Node_12', 4.0, 60, False),
    ('Node_10', 'Node_11', 4.5, 50, False)
]

# 3. معملات المرور
TRAFFIC_MULTIPLIERS = {
    'Low': 1.0,
    'Medium': 1.5,
    'Heavy': 2.5
}