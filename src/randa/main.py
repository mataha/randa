# Copyright (c) mataha and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import argparse
import multiprocessing
import os
import sys

from typing import Sequence

import aiohttp
import dotenv
import ujson

from randa.client import DefaultIntentsClient

def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--once", "-1", action="store_true")

    args = parser.parse_args(argv)

    dotenv.load_dotenv(override=True)

    token = os.getenv("RANDA_DISCORD_TOKEN") or "xxx"

    client = DefaultIntentsClient()

    @client.event
    async def on_ready() -> None:

        payload = {"token": os.getenv("RANDA_D2RW_TOKEN")}
        url = "https://d2runewizard.com/api/terror-zone"
        headers = {
            "D2R-Contact": "mataha@users.noreply.github.com",
            "D2R-Platform": "Discord",
            "D2R-Repo": "https://github.com/mataha/randa"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=payload, headers=headers) as response:
                json = await response.json(loads=ujson.loads)

                # map properly somewhere else later
                data = json["terrorZone"]
                provider = json["providedBy"]
                # probably better from here than directly from `.zone`, right
                zone = data["highestProbabilityZone"]["zone"]
                act = str(data["highestProbabilityZone"]["act"])[3:] # ugly AF
                confidence = float(data["highestProbabilityZone"]["probability"])

                id_ = int(os.getenv("RANDA_DISCORD_CHANNELS") or 0)
                channel = client.get_channel(id_)

                if channel:
                    text = (
                        f"{zone} in Act {act} with {confidence:.2%} confidence; "
                        f"provided by {provider}"
                    )
                    await channel.send(content=text, suppress_embeds=True)

        if args.once:
            await client.close()

    client.run(token)

    return 0


if __name__ == '__main__':
    multiprocessing.freeze_support()
    raise SystemExit(main())
