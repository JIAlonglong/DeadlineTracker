"""
计算机科学 / 机器人学 顶会与期刊截稿日期数据库
数据为历年典型截止日期，每年可能会微调，建议定期更新。
"""

from datetime import date


def _d(year, month, day):
    return date(year, month, day)


CONFERENCES = {
    # ======================== 机器学习 / AI ========================
    "NeurIPS": {
        "full_name": "Neural Information Processing Systems",
        "category": "ML/AI",
        "typical_month": 5,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 5, 22), "note": "Abstract deadline"},
            {"year": 2026, "deadline": _d(2026, 5, 29), "note": "Full paper"},
        ],
    },
    "ICML": {
        "full_name": "International Conference on Machine Learning",
        "category": "ML/AI",
        "typical_month": 1,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 1, 31), "note": "Main conference"},
        ],
    },
    "ICLR": {
        "full_name": "International Conference on Learning Representations",
        "category": "ML/AI",
        "typical_month": 10,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 10, 1), "note": "Submission"},
        ],
    },
    "AAAI": {
        "full_name": "AAAI Conference on Artificial Intelligence",
        "category": "AI",
        "typical_month": 8,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 8, 15), "note": "Abstract"},
            {"year": 2026, "deadline": _d(2026, 8, 22), "note": "Full paper"},
        ],
    },
    "IJCAI": {
        "full_name": "International Joint Conference on AI",
        "category": "AI",
        "typical_month": 1,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 1, 23), "note": "Abstract"},
            {"year": 2026, "deadline": _d(2026, 1, 30), "note": "Full paper"},
        ],
    },
    "AISTATS": {
        "full_name": "AI & Statistics",
        "category": "ML/Stats",
        "typical_month": 10,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 10, 6), "note": "Submission"},
        ],
    },
    # ======================== 计算机视觉 ========================
    "CVPR": {
        "full_name": "Computer Vision and Pattern Recognition",
        "category": "CV",
        "typical_month": 11,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 11, 14), "note": "Submission (for 2027)"},
        ],
    },
    "ICCV": {
        "full_name": "International Conference on Computer Vision",
        "category": "CV",
        "typical_month": 3,
        "rounds": [
            {"year": 2027, "deadline": _d(2027, 3, 8), "note": "Submission"},
        ],
    },
    "ECCV": {
        "full_name": "European Conference on Computer Vision",
        "category": "CV",
        "typical_month": 3,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 3, 6), "note": "Submission"},
        ],
    },
    # ======================== 机器人 ========================
    "ICRA": {
        "full_name": "IEEE Int. Conf. on Robotics and Automation",
        "category": "Robotics",
        "typical_month": 9,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 9, 15), "note": "Submission"},
        ],
    },
    "IROS": {
        "full_name": "IEEE/RSJ Int. Conf. on Intelligent Robots",
        "category": "Robotics",
        "typical_month": 3,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 3, 1), "note": "Submission"},
        ],
    },
    "RSS": {
        "full_name": "Robotics: Science and Systems",
        "category": "Robotics",
        "typical_month": 2,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 2, 1), "note": "Submission"},
        ],
    },
    "CoRL": {
        "full_name": "Conf. on Robot Learning",
        "category": "Robotics/ML",
        "typical_month": 6,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 6, 20), "note": "Submission"},
        ],
    },
    # ======================== NLP ========================
    "ACL": {
        "full_name": "Association for Computational Linguistics",
        "category": "NLP",
        "typical_month": 1,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 1, 17), "note": "Submission"},
        ],
    },
    "EMNLP": {
        "full_name": "Empirical Methods in NLP",
        "category": "NLP",
        "typical_month": 6,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 6, 15), "note": "Submission"},
        ],
    },
    "NAACL": {
        "full_name": "North American Chapter of ACL",
        "category": "NLP",
        "typical_month": 10,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 10, 15), "note": "Submission"},
        ],
    },
    # ======================== 自然语言 / 搜索 ========================
    "COLT": {
        "full_name": "Conf. on Learning Theory",
        "category": "ML/Theory",
        "typical_month": 2,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 2, 7), "note": "Submission"},
        ],
    },
    # ======================== 系统 / 网络 ========================
    "SIGCOMM": {
        "full_name": "ACM Special Interest Group on Data Communication",
        "category": "Networking",
        "typical_month": 1,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 1, 17), "note": "Submission"},
        ],
    },
    "MobiCom": {
        "full_name": "ACM Int. Conf. on Mobile Computing",
        "category": "Mobile/Systems",
        "typical_month": 3,
        "rounds": [
            {"year": 2026, "deadline": _d(2026, 3, 15), "note": "Spring deadline"},
            {"year": 2026, "deadline": _d(2026, 7, 15), "note": "Summer deadline"},
        ],
    },
    # ======================== 顶级期刊 ========================
    "T-PAMI": {
        "full_name": "IEEE Trans. on Pattern Analysis and Machine Intelligence",
        "category": "Journal/CV",
        "typical_month": 0,  # 滚动投稿
        "rounds": [],
    },
    "T-RO": {
        "full_name": "IEEE Trans. on Robotics",
        "category": "Journal/Robotics",
        "typical_month": 0,
        "rounds": [],
    },
    "IJRR": {
        "full_name": "Int. Journal of Robotics Research",
        "category": "Journal/Robotics",
        "typical_month": 0,
        "rounds": [],
    },
    "JMLR": {
        "full_name": "Journal of Machine Learning Research",
        "category": "Journal/ML",
        "typical_month": 0,
        "rounds": [],
    },
    "Nature Machine Intelligence": {
        "full_name": "Nature Machine Intelligence",
        "category": "Journal/ML",
        "typical_month": 0,
        "rounds": [],
    },
}


CATEGORIES = sorted(set(v["category"] for v in CONFERENCES.values()))
