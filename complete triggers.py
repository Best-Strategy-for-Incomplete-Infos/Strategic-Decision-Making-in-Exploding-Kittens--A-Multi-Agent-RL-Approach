TRIGGERS_BOMB_VISIBLE = {
    # --- Bomb on TOP (position 1) ---
    
    # Have Skip
    "DRAW_BOMB_TOP_SKIP_DEFUSE": {
        "actions": ["draw", "skip", "attack", "shuffle"],
        "description": "Bomb on top, have Skip and Defuse",
        "key_question": "Save Defuse or save Skip?"
    },
    "DRAW_BOMB_TOP_SKIP_NO_DEFUSE": {
        "actions": ["skip"],  # Must skip
        "description": "Bomb on top, have Skip, no Defuse",
        "key_question": "Must use Skip to survive"
    },
    
    # Have Attack (no Skip)
    "DRAW_BOMB_TOP_NO_SKIP_ATTACK_DEFUSE": {
        "actions": ["draw", "attack", "shuffle"],
        "description": "Bomb on top, have Attack and Defuse, no Skip",
        "key_question": "Use Defuse or Attack?"
    },
    "DRAW_BOMB_TOP_NO_SKIP_ATTACK_NO_DEFUSE": {
        "actions": ["attack"],  # Must attack
        "description": "Bomb on top, have Attack, no Defuse, no Skip",
        "key_question": "Must use Attack to survive"
    },
    
    # Have Shuffle only (no Skip, no Attack)
    "DRAW_BOMB_TOP_NO_SKIP_NO_ATTACK_SHUFFLE_DEFUSE": {
        "actions": ["draw", "shuffle"],
        "description": "Bomb on top, only have Shuffle and Defuse",
        "key_question": "Shuffle then draw, or just use Defuse?"
    },
    "DRAW_BOMB_TOP_NO_SKIP_NO_ATTACK_SHUFFLE_NO_DEFUSE": {
        "actions": ["shuffle"],  # Must shuffle and pray
        "description": "Bomb on top, only have Shuffle, no Defuse",
        "key_question": "Shuffle and hope"
    },
    
    # Have nothing useful
    "DRAW_BOMB_TOP_NOTHING_DEFUSE": {
        "actions": ["draw"],  # Use Defuse
        "description": "Bomb on top, have Defuse, no action cards",
        "key_question": "Must draw and use Defuse"
    },
    "DRAW_BOMB_TOP_NOTHING_NO_DEFUSE": {
        "actions": ["draw"],  # Death
        "description": "Bomb on top, no Defuse, no action cards",
        "key_question": "Certain death - no decision"
    },
    
    # --- Bomb on SECOND (position 2) ---
    # Draw is safe, but next draw is bomb
    
    "DRAW_BOMB_2ND_SKIP_DEFUSE": {
        "actions": ["draw", "skip", "attack", "shuffle"],
        "description": "Bomb on 2nd, have Skip and Defuse",
        "key_question": "Draw safe card, or save it for others?"
    },
    "DRAW_BOMB_2ND_SKIP_NO_DEFUSE": {
        "actions": ["draw", "skip", "attack", "shuffle"],
        "description": "Bomb on 2nd, have Skip, no Defuse",
        "key_question": "Draw safe card (bomb moves to top for next turn)"
    },
    "DRAW_BOMB_2ND_NO_SKIP_ATTACK_DEFUSE": {
        "actions": ["draw", "attack", "shuffle"],
        "description": "Bomb on 2nd, have Attack and Defuse, no Skip",
        "key_question": "Draw safe card or attack?"
    },
    "DRAW_BOMB_2ND_NO_SKIP_ATTACK_NO_DEFUSE": {
        "actions": ["draw", "attack", "shuffle"],
        "description": "Bomb on 2nd, have Attack, no Skip, no Defuse",
        "key_question": "Draw safe card, bomb goes to top next"
    },
    "DRAW_BOMB_2ND_NO_ACTION_DEFUSE": {
        "actions": ["draw"],
        "description": "Bomb on 2nd, no action cards, have Defuse",
        "key_question": "Draw safe card"
    },
    "DRAW_BOMB_2ND_NO_ACTION_NO_DEFUSE": {
        "actions": ["draw"],
        "description": "Bomb on 2nd, no action cards, no Defuse",
        "key_question": "Draw safe card, dangerous next turn"
    },
    
    # --- Bomb on THIRD (position 3) ---
    # Very similar to 2nd, but more breathing room
    
    "DRAW_BOMB_3RD_HAS_ACTIONS": {
        "actions": ["draw", "skip", "attack", "shuffle"],
        "description": "Bomb on 3rd, have action cards",
        "key_question": "Draw safe card, save actions"
    },
    "DRAW_BOMB_3RD_NO_ACTIONS": {
        "actions": ["draw"],
        "description": "Bomb on 3rd, no action cards",
        "key_question": "Draw safe card"
    },
}


# ============================================================
# CATEGORY 2: ABOUT TO DRAW - BOMB UNKNOWN (BY RISK LEVEL)
# ============================================================
# No information about bomb position
# Key variables: risk_level × has_skip × has_attack × has_defuse

TRIGGERS_BOMB_UNKNOWN = {
    # --- LOW RISK (<10%) ---
    
    "DRAW_UNKNOWN_LOW_HAS_ESCAPE_HAS_DEFUSE": {
        "actions": ["draw", "skip", "attack"],
        "risk": "<10%",
        "description": "Low risk, have Skip/Attack and Defuse",
        "key_question": "Save cards (risk is low)"
    },
    "DRAW_UNKNOWN_LOW_HAS_ESCAPE_NO_DEFUSE": {
        "actions": ["draw", "skip", "attack"],
        "risk": "<10%",
        "description": "Low risk, have Skip/Attack, no Defuse",
        "key_question": "Probably draw, save escape for later"
    },
    "DRAW_UNKNOWN_LOW_NO_ESCAPE_HAS_DEFUSE": {
        "actions": ["draw"],
        "risk": "<10%",
        "description": "Low risk, no escape, have Defuse",
        "key_question": "Just draw (low risk)"
    },
    "DRAW_UNKNOWN_LOW_NO_ESCAPE_NO_DEFUSE": {
        "actions": ["draw"],
        "risk": "<10%",
        "description": "Low risk, no escape, no Defuse",
        "key_question": "Just draw (low risk, no choice)"
    },
    
    # --- MEDIUM RISK (10-25%) ---
    
    "DRAW_UNKNOWN_MED_HAS_ESCAPE_HAS_DEFUSE": {
        "actions": ["draw", "skip", "attack"],
        "risk": "10-25%",
        "description": "Medium risk, have escape and Defuse",
        "key_question": "Draw with Defuse backup, or escape?"
    },
    "DRAW_UNKNOWN_MED_HAS_ESCAPE_NO_DEFUSE": {
        "actions": ["draw", "skip", "attack"],
        "risk": "10-25%",
        "description": "Medium risk, have escape, no Defuse",
        "key_question": "Getting risky - consider escaping"
    },
    "DRAW_UNKNOWN_MED_NO_ESCAPE_HAS_DEFUSE": {
        "actions": ["draw"],
        "risk": "10-25%",
        "description": "Medium risk, no escape, have Defuse",
        "key_question": "Draw with Defuse backup"
    },
    "DRAW_UNKNOWN_MED_NO_ESCAPE_NO_DEFUSE": {
        "actions": ["draw"],
        "risk": "10-25%",
        "description": "Medium risk, no escape, no Defuse",
        "key_question": "Risky but no choice"
    },
    
    # --- HIGH RISK (25-40%) ---
    
    "DRAW_UNKNOWN_HIGH_HAS_ESCAPE_HAS_DEFUSE": {
        "actions": ["draw", "skip", "attack"],
        "risk": "25-40%",
        "description": "High risk, have escape and Defuse",
        "key_question": "Escape or use Defuse as backup?"
    },
    "DRAW_UNKNOWN_HIGH_HAS_ESCAPE_NO_DEFUSE": {
        "actions": ["skip", "attack"],  # Should escape
        "risk": "25-40%",
        "description": "High risk, have escape, no Defuse",
        "key_question": "Should use escape card"
    },
    "DRAW_UNKNOWN_HIGH_NO_ESCAPE_HAS_DEFUSE": {
        "actions": ["draw"],
        "risk": "25-40%",
        "description": "High risk, no escape, have Defuse",
        "key_question": "Draw with Defuse ready"
    },
    "DRAW_UNKNOWN_HIGH_NO_ESCAPE_NO_DEFUSE": {
        "actions": ["draw"],
        "risk": "25-40%",
        "description": "High risk, no escape, no Defuse",
        "key_question": "Dangerous - pray"
    },
    
    # --- CRITICAL RISK (>40%) ---
    
    "DRAW_UNKNOWN_CRIT_HAS_ESCAPE_HAS_DEFUSE": {
        "actions": ["skip", "attack", "draw"],
        "risk": ">40%",
        "description": "Critical risk, have escape and Defuse",
        "key_question": "Almost certainly should escape"
    },
    "DRAW_UNKNOWN_CRIT_HAS_ESCAPE_NO_DEFUSE": {
        "actions": ["skip", "attack"],  # Must escape
        "risk": ">40%",
        "description": "Critical risk, have escape, no Defuse",
        "key_question": "Must escape"
    },
    "DRAW_UNKNOWN_CRIT_NO_ESCAPE_HAS_DEFUSE": {
        "actions": ["draw"],
        "risk": ">40%",
        "description": "Critical risk, no escape, have Defuse",
        "key_question": "Draw and likely use Defuse"
    },
    "DRAW_UNKNOWN_CRIT_NO_ESCAPE_NO_DEFUSE": {
        "actions": ["draw"],
        "risk": ">40%",
        "description": "Critical risk, no escape, no Defuse",
        "key_question": "Likely death"
    },
}


# ============================================================
# CATEGORY 3: SHOULD I USE SEE THE FUTURE?
# ============================================================
# Before drawing, should I use See the Future to check?
# Key variables: risk_level × have_escape_cards

TRIGGERS_SEE_FUTURE = {
    "SEE_FUTURE_LOW_RISK_HAS_ESCAPE": {
        "actions": ["see_future", "draw", "skip", "attack"],
        "risk": "<10%",
        "description": "Have See Future, low risk, have escape",
        "key_question": "Save See Future for later (low risk now)"
    },
    "SEE_FUTURE_LOW_RISK_NO_ESCAPE": {
        "actions": ["see_future", "draw"],
        "risk": "<10%",
        "description": "Have See Future, low risk, no escape",
        "key_question": "Information useless without escape - save it or use it?"
    },
    "SEE_FUTURE_MED_RISK_HAS_ESCAPE": {
        "actions": ["see_future", "draw", "skip", "attack"],
        "risk": "10-25%",
        "description": "Have See Future, medium risk, have escape",
        "key_question": "Good time to use - can act on info"
    },
    "SEE_FUTURE_MED_RISK_NO_ESCAPE": {
        "actions": ["see_future", "draw"],
        "risk": "10-25%",
        "description": "Have See Future, medium risk, no escape",
        "key_question": "Info helps but can't act on it"
    },
    "SEE_FUTURE_HIGH_RISK_HAS_ESCAPE": {
        "actions": ["see_future", "skip", "attack"],
        "risk": ">25%",
        "description": "Have See Future, high risk, have escape",
        "key_question": "Use it - need to know before deciding"
    },
    "SEE_FUTURE_HIGH_RISK_NO_ESCAPE": {
        "actions": ["see_future", "draw"],
        "risk": ">25%",
        "description": "Have See Future, high risk, no escape",
        "key_question": "Might as well look (no escape anyway)"
    },
}


# ============================================================
# CATEGORY 4: UNDER ATTACK (MULTIPLE TURNS)
# ============================================================
# Someone played Attack on me, I must take 2+ turns
# Key variables: turns_remaining × has_skip × has_attack × has_defuse

TRIGGERS_ATTACKED = {
    # --- 2 TURNS REMAINING ---
    
    "ATTACKED_2_TURNS_HAS_SKIP_HAS_ATTACK_DEFUSE": {
        "actions": ["draw", "skip", "attack"],
        "turns": 2,
        "description": "2 turns, have Skip, Attack, Defuse",
        "key_question": "Skip (end 1 turn) or Attack (end all, pass to next)?"
    },
    "ATTACKED_2_TURNS_HAS_SKIP_HAS_ATTACK_NO_DEFUSE": {
        "actions": ["skip", "attack"],
        "turns": 2,
        "description": "2 turns, have Skip and Attack, no Defuse",
        "key_question": "Skip or Attack back?"
    },
    "ATTACKED_2_TURNS_HAS_SKIP_NO_ATTACK_DEFUSE": {
        "actions": ["draw", "skip"],
        "turns": 2,
        "description": "2 turns, have Skip and Defuse, no Attack",
        "key_question": "Skip ends 1 turn, still need 1 more draw"
    },
    "ATTACKED_2_TURNS_HAS_SKIP_NO_ATTACK_NO_DEFUSE": {
        "actions": ["skip", "draw"],
        "turns": 2,
        "description": "2 turns, only Skip, no Defuse",
        "key_question": "Skip then risky draw"
    },
    "ATTACKED_2_TURNS_NO_SKIP_HAS_ATTACK_DEFUSE": {
        "actions": ["draw", "attack"],
        "turns": 2,
        "description": "2 turns, have Attack and Defuse, no Skip",
        "key_question": "Attack back (ends all turns) or draw twice?"
    },
    "ATTACKED_2_TURNS_NO_SKIP_HAS_ATTACK_NO_DEFUSE": {
        "actions": ["attack"],  # Should attack back
        "turns": 2,
        "description": "2 turns, only Attack, no Defuse",
        "key_question": "Attack back to survive"
    },
    "ATTACKED_2_TURNS_NOTHING_DEFUSE": {
        "actions": ["draw"],
        "turns": 2,
        "description": "2 turns, no escape cards, have Defuse",
        "key_question": "Draw twice, Defuse once if needed"
    },
    "ATTACKED_2_TURNS_NOTHING_NO_DEFUSE": {
        "actions": ["draw"],
        "turns": 2,
        "description": "2 turns, no escape, no Defuse",
        "key_question": "Very dangerous - double draw"
    },
    
    # --- 3+ TURNS REMAINING ---
    
    "ATTACKED_3PLUS_HAS_ATTACK": {
        "actions": ["attack"],
        "turns": "3+",
        "description": "3+ turns, have Attack",
        "key_question": "Definitely attack back"
    },
    "ATTACKED_3PLUS_HAS_SKIP_NO_ATTACK": {
        "actions": ["skip", "draw"],
        "turns": "3+",
        "description": "3+ turns, have Skip, no Attack",
        "key_question": "Skip helps but still need 2+ draws"
    },
    "ATTACKED_3PLUS_NOTHING": {
        "actions": ["draw"],
        "turns": "3+",
        "description": "3+ turns, no escape cards",
        "key_question": "Very dangerous"
    },
}


# ============================================================
# CATEGORY 5: JUST DEFUSED - WHERE TO PLACE BOMB
# ============================================================
# I survived an explosion, now where do I put the bomb?
# Key variables: players_alive × my_position × know_opponent_hands

TRIGGERS_DEFUSED = {
    # --- 2 PLAYERS ---
    
    "DEFUSED_2P": {
        "actions": ["place_top", "place_2nd", "place_3rd", "place_middle", "place_bottom"],
        "players": 2,
        "description": "2 players, just defused",
        "key_question": "Top = opponent draws next. Bottom = safe for now."
    },
    
    # --- 3 PLAYERS ---
    
    "DEFUSED_3P_I_AM_WEAKEST": {
        "actions": ["place_top", "place_2nd", "place_3rd", "place_middle", "place_bottom"],
        "players": 3,
        "description": "3 players, I'm weakest",
        "key_question": "Target the strongest player"
    },
    "DEFUSED_3P_I_AM_MIDDLE": {
        "actions": ["place_top", "place_2nd", "place_3rd", "place_middle", "place_bottom"],
        "players": 3,
        "description": "3 players, I'm middle",
        "key_question": "Target strongest or random?"
    },
    "DEFUSED_3P_I_AM_STRONGEST": {
        "actions": ["place_top", "place_2nd", "place_3rd", "place_middle", "place_bottom"],
        "players": 3,
        "description": "3 players, I'm strongest",
        "key_question": "Hide it deep or target someone?"
    },
    
    # --- 4 PLAYERS ---
    
    "DEFUSED_4P_I_AM_WEAKEST": {
        "actions": ["place_top", "place_for_player_2", "place_for_player_3", "place_middle", "place_bottom"],
        "players": 4,
        "description": "4 players, I'm weakest",
        "key_question": "Target strongest (player 2 or 3 away)"
    },
    "DEFUSED_4P_I_AM_STRONGEST": {
        "actions": ["place_top", "place_for_player_2", "place_for_player_3", "place_middle", "place_bottom"],
        "players": 4,
        "description": "4 players, I'm strongest",
        "key_question": "Hide it or target specific player?"
    },
    "DEFUSED_4P_I_AM_MIDDLE": {
        "actions": ["place_top", "place_for_player_2", "place_for_player_3", "place_middle", "place_bottom"],
        "players": 4,
        "description": "4 players, I'm middle",
        "key_question": "Target or neutral?"
    },
    
    # --- 5 PLAYERS ---
    
    "DEFUSED_5P_I_AM_WEAKEST": {
        "actions": ["place_top", "place_for_player_2", "place_for_player_3", "place_for_player_4", "place_bottom"],
        "players": 5,
        "description": "5 players, I'm weakest",
        "key_question": "Target strongest"
    },
    "DEFUSED_5P_OTHER": {
        "actions": ["place_top", "place_for_player_2", "place_for_player_3", "place_for_player_4", "place_bottom"],
        "players": 5,
        "description": "5 players, not weakest",
        "key_question": "Strategic placement"
    },
    
    # --- OPPONENT HAS/DOESN'T HAVE DEFUSE (inferred) ---
    
    "DEFUSED_NEXT_OPPONENT_NO_DEFUSE": {
        "actions": ["place_top"],
        "description": "Next opponent likely has no Defuse",
        "key_question": "Top = likely kill"
    },
    "DEFUSED_NEXT_OPPONENT_HAS_DEFUSE": {
        "actions": ["place_2nd", "place_3rd", "place_middle", "place_bottom"],
        "description": "Next opponent likely has Defuse",
        "key_question": "Don't waste bomb on top"
    },
}


# ============================================================
# CATEGORY 6: RECEIVED FAVOR - WHAT TO GIVE
# ============================================================
# Someone used Favor on me, I must give them a card
# Key variables: my_hand_composition

TRIGGERS_FAVOR = {
    "FAVOR_HAVE_CATS_ONLY": {
        "actions": ["give_cat"],
        "description": "Only have useless cat cards to give",
        "key_question": "Give cat (lowest value)"
    },
    "FAVOR_HAVE_CATS_AND_ACTIONS": {
        "actions": ["give_cat", "give_action"],
        "description": "Have cats and action cards",
        "key_question": "Give cat (keep actions)"
    },
    "FAVOR_HAVE_ACTIONS_NO_CATS": {
        "actions": ["give_skip", "give_attack", "give_shuffle", "give_see", "give_nope"],
        "description": "Only action cards, no cats",
        "key_question": "Give least valuable action"
    },
    "FAVOR_HAVE_DEFUSE_AND_OTHERS": {
        "actions": ["give_other"],
        "description": "Have Defuse and other cards",
        "key_question": "Never give Defuse"
    },
    "FAVOR_ONLY_DEFUSE": {
        "actions": ["give_defuse"],
        "description": "Only have Defuse left",
        "key_question": "Forced to give Defuse"
    },
    "FAVOR_HAVE_DUPLICATES": {
        "actions": ["give_duplicate"],
        "description": "Have duplicate action cards",
        "key_question": "Give duplicate (keep one)"
    },
}


# ============================================================
# CATEGORY 7: CAN NOPE - SHOULD I?
# ============================================================
# Someone played a card, should I Nope it?
# Key variables: action_type × affects_me × nope_count × game_phase

TRIGGERS_NOPE = {
    # --- ATTACK ---
    
    "NOPE_ATTACK_ON_ME_HAVE_1_NOPE": {
        "actions": ["nope", "allow"],
        "description": "Someone attacking me, have 1 Nope",
        "key_question": "Stop attack or save Nope?"
    },
    "NOPE_ATTACK_ON_ME_HAVE_2_NOPE": {
        "actions": ["nope", "allow"],
        "description": "Someone attacking me, have 2+ Nopes",
        "key_question": "Can afford to Nope"
    },
    "NOPE_ATTACK_ON_ME_HAVE_SKIP": {
        "actions": ["nope", "allow"],
        "description": "Someone attacking me, have Skip",
        "key_question": "Skip might be better than Nope"
    },
    "NOPE_ATTACK_ON_OTHERS": {
        "actions": ["nope", "allow"],
        "description": "Someone attacking another player",
        "key_question": "Usually don't intervene"
    },
    
    # --- FAVOR ---
    
    "NOPE_FAVOR_ON_ME": {
        "actions": ["nope", "allow"],
        "description": "Someone using Favor on me",
        "key_question": "Nope to protect hand?"
    },
    "NOPE_FAVOR_ON_OTHERS": {
        "actions": ["nope", "allow"],
        "description": "Someone using Favor on another",
        "key_question": "Usually don't intervene"
    },
    
    # --- SEE FUTURE ---
    
    "NOPE_SEE_FUTURE": {
        "actions": ["nope", "allow"],
        "description": "Someone using See the Future",
        "key_question": "Rarely worth Noping"
    },
    
    # --- SKIP ---
    
    "NOPE_SKIP_BOMB_ON_TOP": {
        "actions": ["nope", "allow"],
        "description": "Someone Skipping, bomb likely on top",
        "key_question": "Force them to draw bomb?"
    },
    "NOPE_SKIP_UNKNOWN": {
        "actions": ["nope", "allow"],
        "description": "Someone Skipping, bomb position unknown",
        "key_question": "Rarely worth Noping"
    },
    
    # --- SHUFFLE ---
    
    "NOPE_SHUFFLE_I_KNOW_DECK": {
        "actions": ["nope", "allow"],
        "description": "Someone shuffling, I know deck order",
        "key_question": "Nope to keep my information"
    },
    "NOPE_SHUFFLE_I_DONT_KNOW": {
        "actions": ["allow"],
        "description": "Someone shuffling, I don't know deck",
        "key_question": "No reason to Nope"
    },
    
    # --- CAT STEAL ---
    
    "NOPE_CAT_STEAL_ON_ME": {
        "actions": ["nope", "allow"],
        "description": "Someone stealing from me with cats",
        "key_question": "Protect valuable cards?"
    },
    "NOPE_CAT_STEAL_ON_OTHERS": {
        "actions": ["nope", "allow"],
        "description": "Someone stealing from another with cats",
        "key_question": "Usually don't intervene"
    },
}


# ============================================================
# CATEGORY 8: PROACTIVE PLAY - USE CARDS BEFORE DRAWING?
# ============================================================
# Before I must draw, should I use Attack/other cards offensively?
# Key variables: my_position × risk_level × action_cards

TRIGGERS_PROACTIVE = {
    # --- I AM WEAKEST ---
    
    "PROACTIVE_WEAKEST_HAS_ATTACK_LOW_RISK": {
        "actions": ["attack", "draw"],
        "description": "I'm weakest, have Attack, low risk",
        "key_question": "Attack strongest to balance game?"
    },
    "PROACTIVE_WEAKEST_HAS_ATTACK_HIGH_RISK": {
        "actions": ["attack"],
        "description": "I'm weakest, have Attack, high risk",
        "key_question": "Attack to avoid risky draw"
    },
    "PROACTIVE_WEAKEST_NO_ATTACK": {
        "actions": ["draw"],
        "description": "I'm weakest, no Attack",
        "key_question": "Just draw"
    },
    
    # --- I AM STRONGEST ---
    
    "PROACTIVE_STRONGEST_HAS_ATTACK_LOW_RISK": {
        "actions": ["draw"],
        "description": "I'm strongest, have Attack, low risk",
        "key_question": "Save Attack, don't draw attention"
    },
    "PROACTIVE_STRONGEST_HAS_ATTACK_HIGH_RISK": {
        "actions": ["attack", "draw"],
        "description": "I'm strongest, have Attack, high risk",
        "key_question": "Use Attack to avoid risk?"
    },
    "PROACTIVE_STRONGEST_NO_ATTACK": {
        "actions": ["draw"],
        "description": "I'm strongest, no Attack",
        "key_question": "Just draw"
    },
    
    # --- I AM MIDDLE ---
    
    "PROACTIVE_MIDDLE_HAS_ATTACK_ANY_RISK": {
        "actions": ["attack", "draw"],
        "description": "I'm middle position, have Attack",
        "key_question": "Stay neutral or attack leader?"
    },
    "PROACTIVE_MIDDLE_NO_ATTACK": {
        "actions": ["draw"],
        "description": "I'm middle, no Attack",
        "key_question": "Just draw"
    },
}


# ============================================================
# CATEGORY 9: ENDGAME (2 PLAYERS, 1 BOMB)
# ============================================================
# Final showdown - every decision is critical
# Key variables: has_defuse × has_skip × has_attack × bomb_prob

TRIGGERS_ENDGAME = {
    "ENDGAME_DEFUSE_SKIP_ATTACK": {
        "actions": ["draw", "skip", "attack"],
        "description": "Endgame: have Defuse, Skip, Attack",
        "key_question": "Full options - optimal play?"
    },
    "ENDGAME_DEFUSE_SKIP_NO_ATTACK": {
        "actions": ["draw", "skip"],
        "description": "Endgame: have Defuse and Skip",
        "key_question": "Skip delays, Defuse survives"
    },
    "ENDGAME_DEFUSE_ATTACK_NO_SKIP": {
        "actions": ["draw", "attack"],
        "description": "Endgame: have Defuse and Attack",
        "key_question": "Attack gives opponent 2 draws"
    },
    "ENDGAME_DEFUSE_NO_ACTIONS": {
        "actions": ["draw"],
        "description": "Endgame: only Defuse",
        "key_question": "Draw until bomb, survive once"
    },
    "ENDGAME_NO_DEFUSE_HAS_SKIP": {
        "actions": ["skip"],
        "description": "Endgame: no Defuse, have Skip",
        "key_question": "Must use Skip to survive"
    },
    "ENDGAME_NO_DEFUSE_HAS_ATTACK": {
        "actions": ["attack"],
        "description": "Endgame: no Defuse, have Attack",
        "key_question": "Must Attack to survive"
    },
    "ENDGAME_NO_DEFUSE_NO_ACTIONS": {
        "actions": ["draw"],
        "description": "Endgame: no Defuse, no actions",
        "key_question": "Pure luck"
    },
    
    # --- ENDGAME WITH KNOWN BOMB ---
    
    "ENDGAME_BOMB_TOP_HAS_ESCAPE": {
        "actions": ["skip", "attack"],
        "description": "Endgame: bomb on top, have escape",
        "key_question": "Must escape"
    },
    "ENDGAME_BOMB_TOP_NO_ESCAPE_HAS_DEFUSE": {
        "actions": ["draw"],
        "description": "Endgame: bomb on top, have Defuse",
        "key_question": "Draw and defuse"
    },
    "ENDGAME_BOMB_TOP_NOTHING": {
        "actions": ["draw"],
        "description": "Endgame: bomb on top, nothing",
        "key_question": "Certain loss"
    },
    "ENDGAME_BOMB_NOT_TOP": {
        "actions": ["draw"],
        "description": "Endgame: know bomb is not on top",
        "key_question": "Safe draw"
    },
}


# ============================================================
# CATEGORY 10: INFERRED INFORMATION
# ============================================================
# Opponent behavior reveals information
# Key variables: opponent_action × context

TRIGGERS_INFERRED = {
    "INFERRED_OPPONENT_SKIPPED_AFTER_SEE": {
        "actions": ["skip", "attack", "shuffle", "draw"],
        "description": "Opponent used See then Skip",
        "key_question": "Bomb likely on top - react"
    },
    "INFERRED_OPPONENT_ATTACKED_AFTER_SEE": {
        "actions": ["skip", "attack", "shuffle", "draw"],
        "description": "Opponent used See then Attack (to me)",
        "key_question": "Bomb likely on top - react"
    },
    "INFERRED_OPPONENT_SHUFFLED_AFTER_SEE": {
        "actions": ["draw"],
        "description": "Opponent used See then Shuffle",
        "key_question": "They saw bomb, shuffled it away"
    },
    "INFERRED_OPPONENT_USED_DEFUSE": {
        "actions": ["note"],
        "description": "Opponent used their Defuse",
        "key_question": "They're vulnerable now - target them?"
    },
    "INFERRED_OPPONENT_MANY_SKIPS": {
        "actions": ["note"],
        "description": "Opponent used many Skips",
        "key_question": "They're running low on escapes"
    },
}


# ============================================================
# SUMMARY COUNTS
# ============================================================

def count_triggers():
    categories = [
        ("Bomb Visible", TRIGGERS_BOMB_VISIBLE),
        ("Bomb Unknown", TRIGGERS_BOMB_UNKNOWN),
        ("See Future", TRIGGERS_SEE_FUTURE),
        ("Under Attack", TRIGGERS_ATTACKED),
        ("Just Defused", TRIGGERS_DEFUSED),
        ("Received Favor", TRIGGERS_FAVOR),
        ("Can Nope", TRIGGERS_NOPE),
        ("Proactive", TRIGGERS_PROACTIVE),
        ("Endgame", TRIGGERS_ENDGAME),
        ("Inferred", TRIGGERS_INFERRED),
    ]
    
    total = 0
    print("TRIGGER COUNT BY CATEGORY")
    print("=" * 40)
    for name, triggers in categories:
        count = len(triggers)
        total += count
        print(f"{name:20}: {count:3} triggers")
    print("=" * 40)
    print(f"{'TOTAL':20}: {total:3} triggers")
    
    return total


if __name__ == "__main__":
    count_triggers()
    
    print("\n\nSAMPLE TRIGGERS:")
    print("=" * 60)
    
    for name, data in list(TRIGGERS_BOMB_VISIBLE.items())[:3]:
        print(f"\n{name}")
        print(f"  Actions: {data['actions']}")
        print(f"  Description: {data['description']}")
        print(f"  Key Question: {data['key_question']}")

