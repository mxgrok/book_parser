

class Helpers:

    @classmethod
    def clean_url(cls, url: str) -> str:
        patterns: tuple = ('.', 'https', 'http', ':', '/', '?', '&', '_', '=')
        for pattern in patterns:
            url = '_'.join(i for i in url.replace(pattern, ' ').split() if i)

        return url