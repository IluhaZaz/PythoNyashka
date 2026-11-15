import logging
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response

from src.match import dependencies
from src.match.domain.schemas import MatchGet, MatchesGetResponse
from src.match.usecase import (
    AcceptMatch,
    GetMatchHistory,
    GetNextMatch,
    MatchNotFoundError,
    RejectMatch,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("", status_code=200)
async def get_match(
    profile_id: str = Query(..., description="Acting profile ID set by the BFF"),
    usecase: GetNextMatch = Depends(dependencies.get_next_match_uc),
) -> MatchGet:
    try:
        match = await usecase.execute(profile_id)
    except MatchNotFoundError:
        return JSONResponse(status_code=404, content={"error": "No matches available"})
    return match


@router.get("/history", status_code=200)
async def get_match_history(
    profile_id: str = Query(..., description="Acting profile ID set by the BFF"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    usecase: GetMatchHistory = Depends(dependencies.get_match_history_uc),
) -> MatchesGetResponse:
    matches = await usecase.execute(profile_id, offset, limit)
    return MatchesGetResponse(matches=matches)


@router.post("/{match_id}/like", status_code=204)
async def accept_match(
    match_id: str,
    profile_id: str = Query(..., description="Acting profile ID set by the BFF"),
    usecase: AcceptMatch = Depends(dependencies.accept_match_uc),
) -> Response:
    try:
        await usecase.execute(match_id, profile_id)
    except MatchNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Match not found"})
    return Response(status_code=204)


@router.post("/{match_id}/dislike", status_code=204)
async def reject_match(
    match_id: str,
    profile_id: str = Query(..., description="Acting profile ID set by the BFF"),
    usecase: RejectMatch = Depends(dependencies.reject_match_uc),
) -> Response:
    try:
        await usecase.execute(match_id, profile_id)
    except MatchNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Match not found"})
    return Response(status_code=204)