class MainResumeEntry:
    def __init__(self, title: str, place: str = None, date: str = None, description: str = None, entry_type: str = ""):
        self.title = title
        self.place = place
        self.date = date
        self.description = description
        self.entry_type = entry_type

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title"),
            place=data.get("place"),
            date=data.get("date"),
            description=data.get("description"),
            entry_type=data.get("entry_type", "")
        )

    def __repr__(self):
        return (f"MainResumeEntry(title='{self.title}', place='{self.place}', "
                f"date='{self.date}', description='{self.description}', entry_type='{self.entry_type}')")


class ResumeDetails:
    def __init__(self, professional_summary="", work_experience=None, personal_projects=None, education=None,
                 skills=None, languages=None, name="", phone_number="", linkedin="", github="", email="", address=""):
        self.professional_summary = professional_summary
        self.work_experience = self._convert_to_entries(work_experience, entry_type="Work Experience")
        self.personal_projects = self._convert_to_entries(personal_projects, entry_type="Personal Project")
        self.education = self._convert_to_entries(education, entry_type="Education")
        self.skills = skills or []
        self.languages = languages or []
        self.name = name
        self.phone_number = phone_number
        self.linkedin = linkedin
        self.github = github
        self.email = email
        self.address = address

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
        """Converts a list of dictionaries to a list of MainResumeEntry objects."""
        if entries is None:
            return []
        return [MainResumeEntry.from_dict({**entry, 'entry_type': entry_type}) for entry in entries]

    def __repr__(self):
        return (f"Resume(Professional Summary='{self.professional_summary}', "
                f"Work Experience={self.work_experience}, "
                f"Personal Projects={self.personal_projects}, "
                f"Education={self.education}, "
                f"Skills={self.skills}, Languages={self.languages}, "
                f"Name='{self.name}', Phone Number='{self.phone_number}', "
                f"LinkedIn='{self.linkedin}', GitHub='{self.github}', "
                f"Email='{self.email}', Address='{self.address}')")