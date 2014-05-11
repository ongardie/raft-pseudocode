#*\codetitle{start new election}*\#
on (state in [FOLLOWER, CANDIDATE] and
    electionAlarm < now()):
| electionAlarm = now() + rand(1.0, 2.0) *
|                         ELECTION_TIMEOUT
| currentTerm += 1
| votedFor = serverID
| state = CANDIDATE
| foreach peer:
| | # reset all state for peer
#*\codetitle{send RequestVote to peer}*\#
on (state == CANDIDATE and
    rpcDue[peer] < now()):
| rpcDue[peer] = now() + RPC_TIMEOUT
| send RequestVote to peer {
|   term: currentTerm,
|   lastLogTerm: logTerm(len(log)),
|   lastLogIndex: len(log)}
#*\codetitle{become leader}*\#
on (state == CANDIDATE and
    sum(voteGranted) + 1 > NUM_SERVERS / 2:
| state = LEADER
| leader = localhost
| foreach peer:
| | nextIndex[peer] = len(log) + 1
#*\codetitle{send AppendEntries to peer}*\#
on (state == LEADER and
    (matchIndex[peer] < len(log) or
     rpcDue[peer] < now()):
| rpcDue[peer] = now() + ELECTION_TIMEOUT / 2
| lastIndex := choose in (nextIndex[peer] - 1)..len(log)
| nextIndex[peer] = lastIndex
| send AppendEntries to peer {
|   term: currentTerm,
|   prevIndex: nextIndex[peer] - 1,
|   prevTerm: getTerm(nextIndex[peer] - 1),
|   entries: log[nextIndex[peer]..lastIndex],
|   commitIndex: commitIndex}
#*\codetitle{advance commit index}*\#
n := sorted(matchIndex + [len(log)])[NUM_SERVERS / 2ish]
on (state == LEADER and
    logTerm(n) == currentTerm):
| commitIndex = n
#*\codetitle{advance state machine}*\#
on lastApplied < commitIndex:
| lastApplied += 1
| result := stateMachine.ap#**\#ply(log[lastApplied])
| if (state == Leader and
|     logTerm(lastApplied) == currentTerm):
| | # send result to client
