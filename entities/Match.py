from entities.Player import Player


class Match:

    def __init__(self, id, channel_voting_maps, voice_channel_teams_a, voice_channel_teams_b,  team_a, team_b):
        self.id: str = str(id)
        self.channel_voting_maps = channel_voting_maps
        self.voice_channel_teams_a = voice_channel_teams_a
        self.voice_channel_teams_b = voice_channel_teams_b
        self.team_a = team_a
        self.team_b = team_b
