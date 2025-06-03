#!/usr/bin/env python3
"""Classes for managing resume details and structure."""

from typing import List, Optional

class MainResumeEntry:
    def __init__(
            self, title: str, place: str = None, date: str = None,
            description: list = None, entry_type: str = ""
    ):
        self.title = title
        self.place = place
        self.date = date
        self.description = description or []
        self.entry_type = entry_type

    @classmethod
    def from_dict(cls, data):
        description = data.get("description")
        if isinstance(description, str):
            description = [
                desc.strip() for desc in description.split('\n') if desc.strip()
            ]
        elif isinstance(description, list):
            description = [str(desc).strip() for desc in description if desc and str(desc).strip()]
        else:
            description = []

        return cls(
            title=data.get("title", "").strip(),
            place=data.get("place", "").strip(),
            date=data.get("date", "").strip(),
            description=description,
            entry_type=data.get("entry_type", "").strip()
        )

    def __repr__(self):
        return (f"MainResumeEntry(title='{self.title}', place='{self.place}', "
                f"date='{self.date}', description={self.description}, entry_type='{self.entry_type}')")


class ResumeDetails:
    def __init__(
            self, professional_summary="", work_experience=None,
            personal_projects=None, education=None, skills=None,
            languages=None, name="", phone_number="", linkedin="",
            github="", email="", address=""
    ):
        self.professional_summary = professional_summary.strip() if professional_summary else ""
        self.work_experience = self._convert_to_entries(work_experience, entry_type="Work Experience")
        self.personal_projects = self._convert_to_entries(personal_projects, entry_type="Personal Project")
        self.education = self._convert_to_entries(education, entry_type="Education")
        self.skills = [skill.strip() for skill in skills] if skills else []
        self.languages = [lang.strip() for lang in languages] if languages else []
        self.name = name.strip() if name else ""
        self.phone_number = phone_number.strip() if phone_number else ""
        self.linkedin = linkedin.strip() if linkedin else ""
        self.github = github.strip() if github else ""
        self.email = email.strip() if email else ""
        self.address = address.strip() if address else ""

    @classmethod
    def from_dict(cls, data):
        """Creates an instance of ResumeDetails from a dictionary."""
        return cls(
            professional_summary=data.get("professional_summary", ""),
            work_experience=data.get("work_experience", []),
            personal_projects=data.get("personal_projects", []),
            education=data.get("education", []),
            skills=data.get("skills", []),
            languages=data.get("languages", []),
            name=data.get("name", ""),
            phone_number=data.get("phone_number", ""),
            linkedin=data.get("linkedin", ""),
            github=data.get("github", ""),
            email=data.get("email", ""),
            address=data.get("address", "")
        )

    def _convert_to_entries(self, entries, entry_type):
        """Converts a list of dictionaries to a list of MainResumeEntry objects, excluding empty entries."""
        if not entries:
            return []
        converted_entries = []
        for entry in entries:
            # Check if entry has any meaningful data
            has_data = any(value for key, value in entry.items() if value and key != 'entry_type')
            if has_data:
                entry['entry_type'] = entry_type
                converted_entry = MainResumeEntry.from_dict(entry)
                converted_entries.append(converted_entry)
        return converted_entries

    def __repr__(self):
        return (f"ResumeDetails(professional_summary='{self.professional_summary}', "
                f"work_experience={self.work_experience}, "
                f"personal_projects={self.personal_projects}, "
                f"education={self.education}, "
                f"skills={self.skills}, languages={self.languages}, "
                f"name='{self.name}', phone_number='{self.phone_number}', "
                f"linkedin='{self.linkedin}', github='{self.github}', "
                f"email='{self.email}', address='{self.address}')")
