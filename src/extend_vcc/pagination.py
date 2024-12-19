from typing import Dict, Generic, List, Optional, Protocol, TypeVar

from .types import PaginatedResponse, PaginationOptions

T = TypeVar("T")
R = TypeVar("R", bound=PaginatedResponse)


class APIClient(Protocol):
    def json_request(
        self, method: str, path: str, data: Optional[Dict] = None
    ) -> Dict: ...


class Paginator(Generic[T, R]):
    def __init__(
        self,
        api: APIClient,
        options: PaginationOptions,
        path: str,
        query: Dict[str, List[str]],
    ):
        self.has_next = True
        self.next_page = options.page
        self.api = api
        self.path = path
        self.query = query

        # Set pagination parameters
        self.query["count"] = [str(options.count)]
        self.query["sortDirection"] = [options.sort_direction.value]
        self.query["sortField"] = [options.sort_field]

    def __iter__(self):
        return self

    def __next__(self) -> R:
        if not self.has_next:
            raise StopIteration

        self.query["page"] = [str(self.next_page)]
        self.next_page += 1

        # Build query string
        query_string = "&".join(f"{k}={','.join(v)}" for k, v in self.query.items())
        path_with_query = f"{self.path}?{query_string}"

        response = self.api.json_request("GET", path_with_query)
        result = response  # This should be properly deserialized to type R

        pagination = result.get_pagination()
        self.has_next = pagination.page < pagination.number_of_pages

        if not self.has_next:
            raise StopIteration

        return result

    def next(self) -> bool:
        return self.has_next
