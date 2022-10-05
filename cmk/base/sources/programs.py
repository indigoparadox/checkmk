#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path
from typing import Final, Optional

from cmk.utils.translations import TranslationOptions
from cmk.utils.type_defs import ExitSpec, HostAddress, HostName, SourceType

import cmk.core_helpers.cache as file_cache
from cmk.core_helpers import FetcherType, ProgramFetcher
from cmk.core_helpers.agent import AgentFileCache, AgentSummarizerDefault
from cmk.core_helpers.cache import FileCacheGlobals, FileCacheMode

from .agent import AgentSource


class ProgramSource(AgentSource):
    def __init__(
        self,
        hostname: HostName,
        ipaddress: Optional[HostAddress],
        *,
        id_: str,  # "agent" or "special_{agentname}"
        persisted_section_dir: Path,
        cache_dir: Path,
        cmdline: str,
        stdin: Optional[str],
        simulation_mode: bool,
        agent_simulator: bool,
        translation: TranslationOptions,
        encoding_fallback: str,
        check_interval: int,
        is_cmc: bool,
        file_cache_max_age: file_cache.MaxAge,
    ) -> None:
        super().__init__(
            hostname,
            ipaddress,
            source_type=SourceType.HOST,
            fetcher_type=FetcherType.PROGRAM,
            id_=id_,
            persisted_section_dir=persisted_section_dir,
            agent_simulator=agent_simulator,
            translation=translation,
            encoding_fallback=encoding_fallback,
            check_interval=check_interval,
        )
        self.file_cache_base_path: Final = cache_dir
        self.simulation_mode: Final = simulation_mode
        self.file_cache_max_age: Final = file_cache_max_age

        self.cmdline: Final = cmdline
        self.stdin: Final = stdin
        self.is_cmc: Final = is_cmc

    def _make_file_cache(self) -> AgentFileCache:
        return AgentFileCache(
            self.hostname,
            base_path=self.file_cache_base_path,
            max_age=self.file_cache_max_age,
            use_outdated=self.simulation_mode or FileCacheGlobals.use_outdated,
            simulation=self.simulation_mode,
            use_only_cache=False,
            file_cache_mode=FileCacheMode.DISABLED
            if FileCacheGlobals.disabled
            else FileCacheMode.READ_WRITE,
        )

    def _make_fetcher(self) -> ProgramFetcher:
        return ProgramFetcher(
            cmdline=self.cmdline,
            stdin=self.stdin,
            is_cmc=self.is_cmc,
        )

    def _make_summarizer(self, *, exit_spec: ExitSpec) -> AgentSummarizerDefault:
        return AgentSummarizerDefault(exit_spec)


class DSProgramSource(ProgramSource):
    pass


class SpecialAgentSource(ProgramSource):
    pass
