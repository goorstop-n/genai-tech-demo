#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Travel Approval Script.
Usage:
    python scripts/travel_approve.py "${name}" "${amount}" "${reason}"
Example:
    python scripts/travel_approve.py "赵六" "1200" "杭州现场部署"
"""

import json
import uuid
import sys
from datetime import datetime


def validate_input(name, amount, reason):
    if not name.strip():
        raise ValueError("name must not be empty")
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except Exception:
        raise ValueError("amount must be a positive number")
    if not reason.strip():
        raise ValueError("reason must not be empty")

    return amount


def mock_travel_submit(name, amount, reason):
    return {
        "request_id": str(uuid.uuid4()),
        "status": 0,
        "message": "Travel submit success.",
        "name": name,
        "amount": amount,
        "reason": reason,
        "created_at": datetime.now().isoformat(),
    }


def main():
    if len(sys.argv) != 4:
        print("Usage: python travel_approve.py \"姓名\" \"金额\" \"差旅事由\"")
        sys.exit(1)

    name = sys.argv[1]
    amount_input = sys.argv[2]
    reason = sys.argv[3]

    try:
        amount = validate_input(name, amount_input, reason)
        result = mock_travel_submit(name, amount, reason)

        print(json.dumps(result, ensure_ascii=False, indent=4))

    except Exception as e:
        error_result = {
            "status": 1,
            "message": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()