#*\codetitle{server state}*\#
# FOLLOWER, CANDIDATE, or LEADER
state := FOLLOWER
# latest term server has seen (increases monotonically)
currentTerm := 1
# candidate that received vote in current term
votedFor := None
# log entries; each entry contains command for state
# machine, and term when entry was received by leader
log := [] # indexed from 1
# index of highest log entry known to be committed
commitIndex := 0
# time after which to start new election
electionAlarm := 0.0
# applies committed commands in log order
stateMachine := new SM()
# identity of last known leader
leader := None

# State per peer, valid only for the current term
foreach peer:
| # time after which to send another RPC
| # (RequestVote or heartbeat)
| rpcDue[peer] := 0.0
| # True if peer has granted this server its vote
| voteGranted[peer] := False
| # index of highest log entry known to be replicated
| # on peer
| matchIndex[peer] := 0
| # index of next log entry to send to peer
| nextIndex[peer] := 1
