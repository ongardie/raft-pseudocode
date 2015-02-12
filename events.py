#*\codetitle{on RequestVote request from peer}*\#
if currentTerm < m.term:
| stepDown(m.term)
if (currentTerm == m.term and
    votedFor in [None, peer] and
    (m.lastLogTerm > logTerm(len(log)) or
    (m.lastLogTerm == logTerm(len(log)) and
     m.lastLogIndex >= len(log)))):
| granted := True
| votedFor = peer
| electionAlarm = now() + rand(1.0, 2.0) *
|                         ELECTION_TIMEOUT
else:
| granted := False
reply {term: currentTerm,
       granted: granted}
#*\codetitle{on RequestVote response from peer}*\#
if currentTerm < m.term:
| stepDown(m.term)
if (state == CANDIDATE and
    currentTerm == m.term):
| rpcDue[peer] = INFINITY
| voteGranted[peer] = m.granted
#*\codetitle{on AppendEntries request from peer}*\#
if currentTerm < m.term:
| stepDown(m.term)
if currentTerm > m.term:
| reply {term: currentTerm,
|        success: False}
else:
| leader = peer
| state = FOLLOWER
| electionAlarm = now() + rand(1.0, 2.0) *
|                         ELECTION_TIMEOUT
| success := (m.prevIndex == 0 or
|   (m.prevIndex <= len(log) and
|    log[m.prevIndex].term == m.prevTerm))
| if success:
| | index := m.prevIndex
| | for j := 1..len(m.entries):
| | | index += 1
| | | if getTerm(index) != m.entries[j].term:
| | | | log = log[1..(index-1)] + m.entries[j]
| | commitIndex = min(m.commitIndex, index)
| else:
| | index = 0
| reply {term: currentTerm,
|        success: success,
|        matchIndex: index}
#*\codetitle{on AppendEntries response from peer}*\#
if currentTerm < m.term:
| stepDown(m.term)
elif state == LEADER and currentTerm == m.term:
| if m.success:
| | matchIndex[peer] = m.matchIndex
| | nextIndex[peer] = m.matchIndex + 1
| else:
| | nextIndex[peer] = max(1, nextIndex[peer] - 1)
#*\codetitle{on StateMachine request from client}*\#
if state == LEADER:
| log.append({term: currentTerm,
|             command: m.command})
#*\codetitle{helper functions}*\#
def stepDown(newTerm):
| currentTerm = newTerm
| state = FOLLOWER
| votedFor = None
| if electionAlarm < now():
| | electionAlarm = now() + rand(1.0, 2.0) *
| |                         ELECTION_TIMEOUT
def logTerm(index):
| if index < 1 or index > len(log):
| | return 0
| else:
| | return log[index].term
